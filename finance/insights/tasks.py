import logging
from datetime import date, timedelta
from decimal import Decimal

from celery import shared_task
from django.contrib.auth import get_user_model
from recurring.models import RecurringTransaction
from transactions.models import Transaction

from .detectors import detect_category_spikes_for_user
from .models import Insight
from .services import create_insight

logger = logging.getLogger(__name__)

DUPLICATE_WINDOW_SECONDS = 60 * 60  # 1 час
DUPLICATE_MIN_AMOUNT = 10  # игнорируем мелкие транзакции (₽)
SUBSCRIPTION_INCREASE_THRESHOLD = 0.02


@shared_task(name="insights.tasks.async_detect_transaction_duplicate")
def async_detect_transaction_duplicate(transaction_id: str):
    """
    Проверяет, есть ли рядом (в окне 5 минут) дубликат указанной транзакции.
    Вызывается сигналом через on_commit + .delay(), чтобы не тормозить bulk-создание.
    """
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
    Проверяет, выросла ли сумма регулярного платежа относительно предыдущего значения.
    old_amount передаётся строкой, чтобы избежать проблем с сериализацией Decimal.
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


@shared_task(name="insights.tasks.detect_category_spikes_all")
def detect_category_spikes_all():
    """
    Раз в день: проверяем скачки трат по категориям у всех активных пользователей.
    Запускается через celery-beat (см. CELERY_BEAT_SCHEDULE).
    """
    today = date.today()
    total = 0
    User = get_user_model()

    for user in User.objects.filter(is_active=True).iterator():
        try:
            total += detect_category_spikes_for_user(user, today)
        except Exception:
            logger.exception("category spike detect failed for user %s", user.id)

    return f"Category spike insights: {total}"
