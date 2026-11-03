from django.utils import timezone

from accounts.models import Account


def maybe_start_grace_period(
    account: Account,
    *,
    require_negative_balance: bool = True,
) -> bool:
    """
    Идемпотентно стартует льготный период кредитной карты.

    Условия:
      — тип счёта = credit_card;
      — grace_period_start ещё не установлен;
      — задан срок льготного периода;
      — (опционально) баланс отрицательный.

    require_negative_balance=False используется из сигнала транзакции,
    потому что в post_save баланс ещё не обновлён — доверяем факту расхода.

    Возвращает True, если дата была установлена.
    """
    if (
        account.account_type != Account.TYPE_CREDIT
        or account.grace_period_start is not None
        or not account.grace_period_days
    ):
        return False

    if require_negative_balance and account.balance >= 0:
        return False

    account.grace_period_start = timezone.localdate()
    account.save(update_fields=["grace_period_start"])
    return True
