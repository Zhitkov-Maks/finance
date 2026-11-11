from datetime import date, datetime, timedelta
from decimal import Decimal

from app_user.models import CustomUser
from celery import shared_task
from django.db import transaction as db_transaction
from django.db.models import F
from django.utils import timezone
from notifications.models import Notification
from notifications.services import create_notification
from transactions.models import Category, Transaction

from accounts.cache import invalidate_balance_history_cache

from .models import Account

DEFAULT_CREDIT_RATE = Decimal("30.0")
DAILY_INTEREST_COMMENT = "Ежедневное начисление процентов по вкладу"
MONTHLY_INTEREST_COMMENT = "Ежемесячное начисление процентов по вкладу"


# =============================================================================
# HELPERS
# =============================================================================


def _get_credit_rate(account: Account) -> Decimal:
    """Возвращает годовую ставку по кредитке или дефолт 30%."""
    return account.credit_rate if account.credit_rate else DEFAULT_CREDIT_RATE


def _get_transaction_time() -> datetime:
    """
    Возвращает timezone-aware время (23:59) текущего дня в локальной TZ.

    Используем timezone.localtime() вместо date.today(), чтобы не получить
    смещение суток при TIME_ZONE ≠ UTC.
    """
    return timezone.localtime().replace(hour=23, minute=59, second=0, microsecond=0)


def _get_or_create_category(
    user: CustomUser, name: str, category_type: str
) -> Category:
    """Ищет или создаёт системную категорию (income/expense)."""
    category, _ = Category.objects.get_or_create(
        user=user, name=name, type_transaction=category_type
    )
    return category


def _apply_balance_operation(
    account: Account,
    amount: Decimal,
    category: Category,
    create_at: datetime,
    comment: str,
    is_income: bool,
) -> None:
    """
    Атомарно создаёт транзакцию и обновляет баланс счёта.

    :param is_income: True — прибавить к балансу, False — вычесть.
    :param create_at: должен быть timezone-aware (для корректной истории и статистики).

    Инвалидация кэша истории баланса выполняется строго после коммита,
    чтобы при откате транзакции кэш не тронулся, а конкурентные читатели
    не закэшировали «промежуточное» состояние.
    """
    with db_transaction.atomic():
        Transaction.objects.create(
            user_id=account.user_id,
            account=account,
            category=category,
            amount=amount,
            create_at=create_at,
            comment=comment,
            type_transaction="income" if is_income else "expense",
        )

        balance_delta = amount if is_income else -amount
        Account.objects.filter(pk=account.pk).update(
            balance=F("balance") + balance_delta
        )

        user_id = account.user_id
        db_transaction.on_commit(
            lambda uid=user_id: invalidate_balance_history_cache(uid)
        )


def _notification_exists(
    user: CustomUser, notification_type: str, account_id: int, today: date
) -> bool:
    """Проверяет, было ли уже отправлено уведомление за сегодня."""
    return Notification.objects.filter(
        user=user,
        notification_type=notification_type,
        data__account_id=account_id,
        data__for_date=str(today),
    ).exists()


# =============================================================================
# ЕЖЕДНЕВНЫЕ ПРОЦЕНТЫ ПО ВКЛАДАМ
# =============================================================================


def _daily_interest_already_accrued(account: Account, today: date) -> bool:
    """
    Идемпотентность: одна транзакция начисления в календарный день на счёт.

    Защищает от двойного начисления при повторном запуске celery beat,
    retry задач или ручном перезапуске.
    """
    return Transaction.objects.filter(
        user_id=account.user_id,
        account=account,
        comment=DAILY_INTEREST_COMMENT,
        create_at__date=today,
    ).exists()


def _accrue_interest_for_account(account: Account, create_at: datetime) -> None:
    """
    Начисляет ежедневный процент для одного вклада.
    Формула: Баланс * (Ставка / 100) / 365 дней.
    """
    daily_rate = account.interest_rate / Decimal("100") / Decimal("365")
    interest_amount = (account.balance * daily_rate).quantize(Decimal("0.01"))

    if interest_amount <= 0:
        return

    category = _get_or_create_category(account.user, "Проценты по вкладу", "income")

    _apply_balance_operation(
        account=account,
        amount=interest_amount,
        category=category,
        create_at=create_at,
        comment=DAILY_INTEREST_COMMENT,
        is_income=True,
    )


@shared_task
def accrue_deposit_interest(create_at: datetime | None = None) -> None:
    """
    Ежедневная задача: начисляет проценты по всем активным вкладам.

    :param create_at: опциональное время транзакции (для backfill/тестов).
                      По умолчанию — «23:59 сегодня» в локальной TZ.
    """
    if create_at is None:
        create_at = _get_transaction_time()
    today = timezone.localtime(create_at).date()

    deposits = (
        Account.objects.filter(
            account_type=Account.TYPE_DEPOSIT,
            deleted_at__isnull=True,
            balance__gt=0,
            interest_rate__gt=0,
        ).select_related("user")  # избегаем N+1 при обращении к account.user
    )

    for account in deposits:
        if _daily_interest_already_accrued(account, today):
            continue
        _accrue_interest_for_account(account, create_at)


# =============================================================================
# КРЕДИТНЫЕ КАРТЫ: ЛЬГОТНЫЙ ПЕРИОД
# =============================================================================


def _notify_grace_period_ending(account: Account, today: date) -> None:
    """
    Напоминание за 3 дня до конца льготного периода — с практическим советом.

    Ключевая мысль: большинство пользователей не знают, что
    частичное погашение НЕ сбрасывает таймер. Только полное.
    """
    if _notification_exists(account.user, "payment_upcoming", account.id, today):
        return

    debt = abs(account.balance)
    rate = _get_credit_rate(account)
    monthly_estimate = (debt * rate / Decimal("100") / Decimal("12")).quantize(
        Decimal("0.01")
    )

    advice = (
        f"Погасите долг {debt} ₽ полностью, чтобы сохранить льготный период. "
        f"Важно: частичное погашение НЕ продлевает беспроцентный период — "
        f"таймер сбрасывается только при полном погашении. "
        f"Если полной суммы нет, внесите минимальный платёж "
        f"(обычно 5–8% от долга), чтобы избежать просрочки. "
        f"После истечения периода проценты начнут начисляться на всю сумму долга — "
        f"около {monthly_estimate} ₽ в месяц при ставке {rate}%."
    )

    create_notification(
        user=account.user,
        notification_type="payment_upcoming",
        title=f"⚡ 3 дня до конца льготного периода: {account.name}",
        message=advice,
        data={
            "url": "/accounts",
            "account_id": account.id,
            "for_date": str(today),
            "debt": str(debt),
            "rate": str(rate),
            "days_left": 3,
        },
    )


def _apply_late_penalty(account: Account, today: date, create_at: datetime) -> None:
    """Начисляет проценты за пользование кредитом после льготного периода."""
    rate = _get_credit_rate(account)
    daily_rate = rate / Decimal("100") / Decimal("365")
    debt = abs(account.balance)
    penalty = (debt * daily_rate).quantize(Decimal("0.01"))

    if penalty <= 0:
        return

    category = _get_or_create_category(
        account.user, "Проценты по кредитной карте", "expense"
    )

    _apply_balance_operation(
        account=account,
        amount=penalty,
        category=category,
        create_at=create_at,
        comment=(
            f"Начисление процентов по кредитной карте "
            f"({rate}% годовых после льготного периода)"
        ),
        is_income=False,
    )

    # Уведомление — не чаще раза в день
    if not _notification_exists(account.user, "budget_warning", account.id, today):
        monthly_estimate = (debt * rate / Decimal("100") / Decimal("12")).quantize(
            Decimal("0.01")
        )
        create_notification(
            user=account.user,
            notification_type="budget_warning",
            title="Проценты по кредитной карте",
            message=(
                f"Льготный период по карте «{account.name}» истёк. "
                f"Начислено за день: {penalty} ₽ (ставка {rate}% годовых). "
                f"За месяц набежит ~{monthly_estimate} ₽. "
                f"Погасите долг полностью, чтобы остановить начисление."
            ),
            data={
                "url": "/accounts",
                "account_id": account.id,
                "for_date": str(today),
                "rate": str(rate),
            },
        )


@shared_task
def check_credit_card_overdue(create_at: datetime | None = None) -> None:
    """
    Ежедневная задача: проверяет кредитные карты.
    Управляет льготным периодом, начисляет пени, отправляет уведомления.

    :param create_at: опциональное время транзакции (для backfill/тестов).
    """
    if create_at is None:
        create_at = _get_transaction_time()
    today = timezone.localtime(create_at).date()

    credit_cards = Account.objects.filter(
        account_type=Account.TYPE_CREDIT,
        deleted_at__isnull=True,
        grace_period_start__isnull=False,
    ).select_related("user")

    for account in credit_cards:
        # Долг погашен — выходим
        if account.balance >= 0:
            continue

        end_date = account.grace_period_start + timedelta(
            days=account.grace_period_days
        )
        days_left = (end_date - today).days

        if days_left == 3:
            _notify_grace_period_ending(account, today)
        elif today > end_date:
            _apply_late_penalty(account, today, create_at)


# =============================================================================
# ЕЖЕМЕСЯЧНЫЕ ПРОЦЕНТЫ ПО ВКЛАДАМ
# =============================================================================


def _monthly_interest_already_accrued(account: Account, today: date) -> bool:
    """
    Идемпотентность: одна транзакция начисления в календарный месяц на счёт.

    Защищает от двойного запуска celery beat / ручного перезапуска.
    """
    return Transaction.objects.filter(
        user_id=account.user_id,
        account=account,
        comment=MONTHLY_INTEREST_COMMENT,
        create_at__year=today.year,
        create_at__month=today.month,
    ).exists()


def _accrue_monthly_interest_for_account(account: Account, create_at: datetime) -> None:
    """
    Начисляет месячный процент для одного вклада
    с ежемесячной капитализацией.
    Формула: Баланс * (Ставка / 100) / 12 месяцев.
    """
    monthly_rate = account.interest_rate / Decimal("100") / Decimal("12")
    interest_amount = (account.balance * monthly_rate).quantize(Decimal("0.01"))

    if interest_amount <= 0:
        return

    category = _get_or_create_category(account.user, "Проценты по вкладу", "income")

    _apply_balance_operation(
        account=account,
        amount=interest_amount,
        category=category,
        create_at=create_at,
        comment=MONTHLY_INTEREST_COMMENT,
        is_income=True,
    )


@shared_task
def accrue_monthly_deposit_interest(create_at: datetime | None = None) -> None:
    """
    Ежемесячная задача: начисляет проценты по вкладам с ежемесячной капитализацией.

    Запускается celery beat 1-го числа каждого месяца в 00:05.
    Начисление идёт за прошедший месяц по текущему балансу счёта
    (т.е. по балансу на конец предыдущего месяца).

    :param create_at: опциональное время транзакции (для backfill/тестов).
    """
    if create_at is None:
        create_at = _get_transaction_time()
    today = timezone.localtime(create_at).date()

    if today.day != 1:
        return

    deposits = Account.objects.filter(
        account_type=Account.TYPE_DEPOSIT_MONTHLY,
        deleted_at__isnull=True,
        balance__gt=0,
        interest_rate__gt=0,
    ).select_related("user")

    for account in deposits:
        if _monthly_interest_already_accrued(account, today):
            continue
        _accrue_monthly_interest_for_account(account, create_at)
