import asyncio
from decimal import Decimal

from .calculator import (
    build_day_ops,
    compute_balance_at_end,
    format_results,
    walk_backwards,
)
from .dates import day_bounds, normalize_range, to_date
from .queries import (
    agg_transactions_after,
    agg_transfers_after,
    fetch_accounts,
    fetch_transactions_in_period,
    fetch_transfers_in_period,
)

ZERO = Decimal(0)


async def build_balance_history(
    user,
    date_from,
    date_to,
    account_id: int | None = None,
    include_inactive: bool = False,
) -> dict:
    """
    Асинхронный расчёт ежедневного баланса счетов пользователя за период.

    :param user: пользователь
    :param date_from: начало периода (включительно)
    :param date_to: конец периода (включительно)
    :param account_id: опционально — только по одному счёту
    :param include_inactive: учитывать неактивные счета
    :return: {"accounts": [...], "results": [...]}
    """
    date_from = to_date(date_from)
    date_to = to_date(date_to)
    date_from, date_to = normalize_range(date_from, date_to)

    # 1. Счета — нужны до остальных запросов, т.к. задают account_ids
    accounts = await fetch_accounts(user, account_id, include_inactive)
    if not accounts:
        return {"accounts": [], "results": []}

    account_ids = [a.pk for a in accounts]
    current_balances = {a.pk: (a.balance or ZERO) for a in accounts}

    _, date_to_dt = day_bounds(date_to)
    period_from_dt, _ = day_bounds(date_from)

    (
        (income_after, expense_after),
        (incoming_after, outgoing_after),
        transactions,
        transfers,
    ) = await asyncio.gather(
        agg_transactions_after(user, account_ids, date_to_dt),
        agg_transfers_after(user, account_ids, date_to_dt),
        fetch_transactions_in_period(user, account_ids, period_from_dt, date_to_dt),
        fetch_transfers_in_period(user, account_ids, period_from_dt, date_to_dt),
    )

    balance_at_end = compute_balance_at_end(
        accounts,
        current_balances,
        income_after,
        expense_after,
        incoming_after,
        outgoing_after,
    )
    day_ops = build_day_ops(account_ids, transactions, transfers)
    daily_balances = walk_backwards(date_from, date_to, balance_at_end, day_ops)
    results = format_results(accounts, date_from, date_to, daily_balances)

    return {
        "accounts": [{"id": a.pk, "name": a.name} for a in accounts],
        "results": results,
    }
