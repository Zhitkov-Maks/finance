from decimal import Decimal

from django.utils import timezone

from accounts.models import Account


def reconcile_grace_period(account: Account, old_balance: Decimal = None) -> None:
    """
    Приводит grace_period_start в соответствие с балансом.
    Вызывается из accounts/views.py при ручном изменении баланса.
    """
    if account.account_type != Account.TYPE_CREDIT:
        return
    if account.balance < 0:
        maybe_start_grace_period(account, old_balance=old_balance)


def maybe_start_grace_period(
    account: Account,
    *,
    old_balance: Decimal = None,
    force_date=None,
    require_negative_balance: bool = True,
) -> bool:
    """
    Идемпотентно стартует льготный период кредитной карты.

    old_balance — баланс до операции. Если он был >= 0, а стал < 0,
    это НОВЫЙ долг, и мы перезаписываем дату.
    Если old_balance < 0 (долг рос), дату НЕ трогаем.
    """
    if account.account_type != Account.TYPE_CREDIT:
        return False
    if not account.grace_period_days:
        return False
    if require_negative_balance and account.balance >= 0:
        return False

    # Если таймер уже идет, проверяем: это продолжение долга или новый?
    if account.grace_period_start is not None:
        if old_balance is not None and old_balance >= 0:
            # Была переплата/ноль, а теперь долг — это новый долг!
            pass
        else:
            # Долг был и остался (или old_balance не передан) — не трогаем
            return False

    account.grace_period_start = force_date or timezone.localdate()
    account.save(update_fields=["grace_period_start"])
    return True
