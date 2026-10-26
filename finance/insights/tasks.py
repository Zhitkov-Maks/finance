import asyncio
import logging
from datetime import date, timedelta
from decimal import Decimal

from asgiref.sync import async_to_sync, sync_to_async
from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from recurring.models import RecurringTransaction
from transactions.models import Transaction

from .detectors import (
    detect_budget_overspends_for_user,
    detect_budget_reallocation_for_user,
    detect_cash_gaps_for_user,
    detect_category_spikes_for_user,
    detect_credit_card_grace_for_user,
    detect_debt_vs_deposit_for_user,
    detect_deposit_forecasts_for_user,
    detect_hidden_leaks_for_user,
    detect_idle_cash_for_user,
    detect_monthly_report_for_user,
    detect_salary_spikes_for_user,
    detect_savings_improved_for_user,
)
from .models import Insight
from .services import create_insight

logger = logging.getLogger(__name__)

USER_BATCH_SIZE = 500
DETECTOR_CONCURRENCY = 10
DUPLICATE_WINDOW_SECONDS = 60 * 60
DUPLICATE_MIN_AMOUNT = 10
SUBSCRIPTION_INCREASE_THRESHOLD = 0.02


@shared_task(name="insights.tasks.detect_idle_cash_all")
def detect_idle_cash_all():
    return _run_detector_task(detect_idle_cash_for_user, "Idle cash")


@shared_task(name="insights.tasks.detect_debt_vs_deposit_all")
def detect_debt_vs_deposit_all():
    return _run_detector_task(detect_debt_vs_deposit_for_user, "Debt vs deposit")


@shared_task(name="insights.tasks.detect_budget_reallocation_all")
def detect_budget_reallocation_all():
    return _run_detector_task(
        detect_budget_reallocation_for_user, "Budget reallocation"
    )


@shared_task(name="insights.tasks.detect_savings_improved_all")
def detect_savings_improved_all():
    """Раз в неделю: проверяем улучшение нормы сбережений."""
    return _run_detector_task(detect_savings_improved_for_user, "Savings improved")


@shared_task(name="insights.tasks.detect_monthly_reports_all")
def detect_monthly_reports_all():
    return _run_detector_task(detect_monthly_report_for_user, "Monthly report")


@shared_task(name="insights.tasks.async_detect_transaction_duplicate")
def async_detect_transaction_duplicate(transaction_id: str):
    """Проверяет, есть ли рядом (в окне 1 час) дубликат указанной транзакции."""
    try:
        instance = Transaction.objects.select_related("user", "category").get(
            pk=transaction_id
        )
    except Transaction.DoesNotExist:
        return

    if not instance.amount or not instance.account_id:
        return
    if instance.amount < DUPLICATE_MIN_AMOUNT:
        return

    window_start = instance.create_at - timedelta(seconds=DUPLICATE_WINDOW_SECONDS)
    window_end = instance.create_at + timedelta(seconds=DUPLICATE_WINDOW_SECONDS)

    candidates = Transaction.objects.filter(
        user_id=instance.user_id,
        account_id=instance.account_id,
        amount=instance.amount,
        create_at__gte=window_start,
        create_at__lte=window_end,
    ).exclude(pk=instance.pk)

    if instance.category_id:
        candidates = candidates.filter(category_id=instance.category_id)

    duplicate = candidates.order_by("create_at").first()
    if not duplicate:
        return

    id1, id2 = sorted([str(instance.pk), str(duplicate.pk)])
    period_key = f"transaction_duplicate:{id1}:{id2}"

    try:
        create_insight(
            user=instance.user,
            insight_type=Insight.TYPE_TRANSACTION_DUPLICATE,
            severity=Insight.SEVERITY_WARNING,
            title="Возможный дубликат транзакции",
            message=(
                f"Найдены две одинаковые транзакции на {instance.amount:.0f} ₽ "
                f"в течение 1 часа. Проверьте, не двойной ли это платёж."
            ),
            data={
                "transaction_ids": [str(instance.pk), str(duplicate.pk)],
                "amount": float(instance.amount),
                "account_id": instance.account_id,
                "category_id": instance.category_id,
                "create_at": instance.create_at.isoformat(),
            },
            action_url="/transactions",
            period_key=period_key,
        )
    except Exception:
        logger.exception(
            "async_detect_transaction_duplicate failed: %s", transaction_id
        )


@shared_task(name="insights.tasks.async_detect_subscription_increase")
def async_detect_subscription_increase(recurring_id: int, old_amount_str: str):
    """
    Проверяет, выросла ли сумма регулярного
    платежа относительно предыдущего значения.
    """
    try:
        old_amount = Decimal(old_amount_str)
    except Exception:
        return
    if old_amount <= 0:
        return

    try:
        instance = RecurringTransaction.objects.select_related("user").get(
            pk=recurring_id
        )
    except RecurringTransaction.DoesNotExist:
        return

    new_amount = instance.amount
    if not new_amount or new_amount <= 0:
        return

    increase_ratio = float(new_amount) / float(old_amount)
    if increase_ratio <= 1 + SUBSCRIPTION_INCREASE_THRESHOLD:
        return

    percent = (increase_ratio - 1) * 100

    try:
        create_insight(
            user=instance.user,
            insight_type=Insight.TYPE_SUBSCRIPTION_INCREASE,
            severity=Insight.SEVERITY_INFO,
            title=f"Подорожала подписка: {instance.title}",
            message=(
                f"Регулярный платёж «{instance.title}» вырос с "
                f"{old_amount:.0f} ₽ до {new_amount:.0f} ₽ (+{percent:.0f}%)."
            ),
            data={
                "recurring_id": instance.id,
                "recurring_title": instance.title,
                "old_amount": float(old_amount),
                "new_amount": float(new_amount),
                "percent": round(percent, 1),
            },
            action_url="/recurring",
            period_key=f"subscription_increase:{instance.id}:{new_amount}",
        )
    except Exception:
        logger.exception("async_detect_subscription_increase failed: %s", recurring_id)


async def _run_one(detector, user, today: date, sem: asyncio.Semaphore, counter: dict):
    """Один юзер — один детектор. Защищаем цикл от падения одного пользователя."""
    async with sem:
        try:
            result = await detector(user, today)
        except Exception:
            logger.exception("%s failed for user %s", detector.__name__, user.pk)
            return
        counter["total"] += result or 0


async def _detect_for_all_active_users(
    detector,
    today: date,
    batch_size: int = USER_BATCH_SIZE,
    concurrency: int = DETECTOR_CONCURRENCY,
) -> int:
    """
    Асинхронно прогоняет async-детектор по всем активным пользователям.

    Батчи ограничивают память и число «холодных» запросов к User.
    Семафор ограничивает количество одновременных DB-соединений.
    """
    User = get_user_model()
    qs = User.objects.filter(is_active=True)
    sem = asyncio.Semaphore(concurrency)
    counter = {"total": 0}

    offset = 0
    while True:
        batch = await sync_to_async(list)(qs[offset : offset + batch_size])
        if not batch:
            break
        await asyncio.gather(
            *(_run_one(detector, user, today, sem, counter) for user in batch)
        )
        offset += batch_size

    return counter["total"]


def _run_detector_task(detector, label: str) -> str:
    """Синхронный мост Celery → async-оркестратор."""
    close_old_connections()
    try:
        total = async_to_sync(_detect_for_all_active_users)(detector, date.today())
        return f"{label}: {total}"
    finally:
        close_old_connections()


@shared_task(name="insights.tasks.detect_category_spikes_all")
def detect_category_spikes_all():
    return _run_detector_task(detect_category_spikes_for_user, "Category spike")


@shared_task(name="insights.tasks.detect_salary_spikes_all")
def detect_salary_spikes_all():
    return _run_detector_task(detect_salary_spikes_for_user, "Salary spike")


@shared_task(name="insights.tasks.detect_hidden_leaks_all")
def detect_hidden_leaks_all():
    return _run_detector_task(detect_hidden_leaks_for_user, "Hidden leak")


@shared_task(name="insights.tasks.detect_budget_overspends_all")
def detect_budget_overspends_all():
    return _run_detector_task(detect_budget_overspends_for_user, "Budget overspend")


@shared_task(name="insights.tasks.detect_cash_gaps_all")
def detect_cash_gaps_all():
    return _run_detector_task(detect_cash_gaps_for_user, "Cash gap")


@shared_task(name="insights.tasks.detect_deposit_forecasts_all")
def detect_deposit_forecasts_all():
    return _run_detector_task(detect_deposit_forecasts_for_user, "Deposit forecast")

@shared_task(name="insights.tasks.detect_credit_card_grace_all")
def detect_credit_card_grace_all():
    return _run_detector_task(detect_credit_card_grace_for_user, "Credit card grace")
