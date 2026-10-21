from datetime import date, datetime, time, timedelta
from decimal import Decimal

from celery import shared_task
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from notifications.models import Notification
from notifications.services import create_notification
from transactions.models import Category, Transaction

from .models import Account


def _get_transaction_time() -> datetime:
    """Возвращает timezone-aware время (23:59) для корректной записи в историю."""
    tz = timezone.get_current_timezone()
    return timezone.make_aware(
        datetime.combine(date.today(), time(hour=23, minute=59)), tz
    )


def _get_or_create_category(user, name: str, category_type: str) -> Category:
    """Ищет или создает системную категорию (доход/расход)."""
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
    Атомарно создает транзакцию и обновляет баланс счета.
    is_income: True - прибавить, False - вычесть.
    """
    with transaction.atomic():
        # 1. Создаем транзакцию
        Transaction.objects.create(
            user=account.user,
            account=account,
            category=category,
            amount=amount,
            create_at=create_at,
            comment=comment,
        )

        # 2. Обновляем баланс на уровне БД (безопасно от race condition)
        balance_delta = amount if is_income else -amount
        Account.objects.filter(pk=account.pk).update(
            balance=F("balance") + balance_delta
        )


def _notification_exists(
    user, notification_type: str, account_id: int, today: date
) -> bool:
    """Проверяет, было ли уже отправлено уведомление за сегодня."""
    return Notification.objects.filter(
        user=user,
        notification_type=notification_type,
        data__account_id=account_id,
        data__for_date=str(today),
    ).exists()


def _accrue_interest_for_account(account: Account, create_at: datetime) -> None:
    """Начисляет ежедневный процент для одного вклада."""
    # Формула: Баланс * (Ставка / 100) / 365 дней
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
        comment="Ежедневное начисление процентов по вкладу",
        is_income=True,
    )


def _reset_grace_period(account: Account) -> None:
    """Сбрасывает таймер льготного периода, если долг погашен."""
    account.grace_period_start = None
    account.save(update_fields=["grace_period_start"])


def _notify_grace_period_ending(account: Account, today: date) -> None:
    """Отправляет push-уведомление о скором конце льготного периода."""
    if _notification_exists(account.user, "payment_upcoming", account.id, today):
        return

    create_notification(
        user=account.user,
        notification_type="payment_upcoming",
        title="Скоро конец льготного периода",
        message=f"Через 3 дня истекает льготный период по карте "
        f"«{account.name}». Погасите долг {abs(account.balance)} ₽, "
        f"чтобы избежать процентов.",
        data={"url": "/accounts", "account_id": account.id, "for_date": str(today)},
    )


def _apply_late_penalty(account: Account, today: date, create_at: datetime) -> None:
    """Начисляет штраф за просрочку и уведомляет об этом."""
    # Пеня (например, 30% годовых)
    penalty_rate = Decimal("30.0") / Decimal("100") / Decimal("365")
    debt = abs(account.balance)
    penalty = (debt * penalty_rate).quantize(Decimal("0.01"))

    if penalty <= 0:
        return

    category = _get_or_create_category(
        account.user, "Штраф по кредитной карте", "expense"
    )

    _apply_balance_operation(
        account=account,
        amount=penalty,
        category=category,
        create_at=create_at,
        comment="Начисление пени за просрочку льготного периода (30% годовых)",
        is_income=False,  # Вычитаем, увеличивая долг
    )

    # Отправляем уведомление о штрафе (раз в день)
    if not _notification_exists(account.user, "budget_warning", account.id, today):
        create_notification(
            user=account.user,
            notification_type="budget_warning",
            title="Штраф по кредитной карте",
            message=f"Льготный период по карте «{account.name}» истек. "
            f"Начислена пеня: {penalty} ₽.",
            data={"url": "/accounts", "account_id": account.id, "for_date": str(today)},
        )


# =============================================================================
# CELERY TASKS (Оркестраторы)
# =============================================================================


@shared_task
def accrue_deposit_interest():
    """Ежедневная задача: начисляет проценты по всем активным вкладам."""
    create_at = _get_transaction_time()

    deposits = Account.objects.filter(
        account_type=Account.TYPE_DEPOSIT,
        is_active=True,
        balance__gt=0,
        interest_rate__gt=0,
    )

    for account in deposits:
        _accrue_interest_for_account(account, create_at)


@shared_task
def check_credit_card_overdue():
    """
    Ежедневная задача: проверяет кредитные карты.
    Управляет льготным периодом, начисляет пени, отправляет уведомления.
    """
    today = date.today()
    create_at = _get_transaction_time()

    credit_cards = Account.objects.filter(
        account_type=Account.TYPE_CREDIT,
        grace_period_start__isnull=False,
    )

    for account in credit_cards:
        # 1. Если баланс >= 0, долг погашен
        if account.balance >= 0:
            _reset_grace_period(account)
            continue

        end_date = account.grace_period_start + timedelta(
            days=account.grace_period_days
        )
        days_left = (end_date - today).days

        # 2. Напоминаем за 3 дня до конца
        if days_left == 3:
            _notify_grace_period_ending(account, today)

        # 3. Льготный период истек! Начисляем пеню
        elif today > end_date:
            _apply_late_penalty(account, today, create_at)
