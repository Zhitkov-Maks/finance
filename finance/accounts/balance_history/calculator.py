from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone


def compute_balance_at_end(
    accounts,
    current_balances,
    income_after,
    expense_after,
    incoming_after,
    outgoing_after,
) -> dict[int, Decimal]:
    """
    Откатывает текущие балансы назад к концу date_to:
    убираем доходы/входящие, возвращаем расходы/исходящие.
    """
    zero = Decimal(0)
    result = {}
    for acc in accounts:
        pk = acc.pk
        result[pk] = (
            current_balances.get(pk, zero)
            - income_after.get(pk, zero)
            + expense_after.get(pk, zero)
            - incoming_after.get(pk, zero)
            + outgoing_after.get(pk, zero)
        )
    return result


def build_day_ops(
    account_ids, transactions, transfers
) -> dict[date, dict[int, Decimal]]:
    """
    Раскладывает операции по дням: day_ops[day][acc_id] = дельта.
    """
    account_ids = set(account_ids)
    day_ops: dict[date, dict[int, Decimal]] = defaultdict(lambda: defaultdict(Decimal))

    for tx in transactions:
        day = timezone.localtime(tx["create_at"]).date()
        amount = tx["amount"] or Decimal(0)
        if tx["category__type_transaction"] == "income":
            day_ops[day][tx["account_id"]] += amount
        else:
            day_ops[day][tx["account_id"]] -= amount

    for tr in transfers:
        day = timezone.localtime(tr["timestamp"]).date()
        amount = tr["amount"] or Decimal(0)
        src = tr["source_account_id"]
        dst = tr["destination_account_id"]
        if src in account_ids:
            day_ops[day][src] -= amount
        if dst in account_ids:
            day_ops[day][dst] += amount

    return day_ops


def walk_backwards(
    date_from: date,
    date_to: date,
    balance_at_end: dict[int, Decimal],
    day_ops: dict[date, dict[int, Decimal]],
) -> dict[date, dict[int, Decimal]]:
    """
    Идёт от date_to к date_from, накапливая баланс на конец каждого дня.
    """
    daily_balances: dict[date, dict[int, Decimal]] = {}
    running = dict(balance_at_end)

    current = date_to
    while current >= date_from:
        daily_balances[current] = dict(running)
        for acc_id, delta in day_ops.get(current, {}).items():
            running[acc_id] = running.get(acc_id, Decimal(0)) - delta
        current -= timedelta(days=1)

    return daily_balances


def format_results(accounts, date_from, date_to, daily_balances):
    """Приводит результат к списку словарей."""
    results = []
    current = date_from
    while current <= date_to:
        balances_by_acc = daily_balances.get(current, {})
        acc_map = {}
        total = Decimal(0)
        for acc in accounts:
            val = balances_by_acc.get(acc.pk, Decimal(0))
            acc_map[str(acc.pk)] = float(val)
            total += val
        results.append(
            {
                "date": current.isoformat(),
                "accounts": acc_map,
                "total": float(total),
            }
        )
        current += timedelta(days=1)
    return results
