from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from accounts.models import Account
from django.utils import timezone
from transactions.models import Transaction
from transfer.models import Transfer


def compute_balance_at_end(
    accounts: list[Account],
    current_balances: dict[int, Decimal],
    income_after: dict[int, Decimal],
    expense_after: dict[int, Decimal],
    incoming_after: dict[int, Decimal],
    outgoing_after: dict[int, Decimal],
) -> dict[int, Decimal]:
    """
    Откатывает текущие балансы назад к концу date_to:
    убираем доходы/входящие, возвращаем расходы/исходящие.
    """
    zero = Decimal(0)
    result: dict[int, Decimal] = {}
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


def _extract_day_and_amount(record, ts_field: str) -> tuple[date, Decimal]:
    """День (в локальной TZ) и сумма операции из записи."""
    day = timezone.localtime(record[ts_field]).date()
    amount = record["amount"] or Decimal(0)
    return day, amount


def _apply_delta(
    day_ops: dict[date, dict[int, Decimal]],
    day: date,
    account_id: int,
    delta: Decimal,
    allowed_ids: set[int] | None = None,
) -> None:
    """Прибавляет delta к счёту за день.

    Если allowed_ids задано — операция применяется только для счетов из этого множества
    (так фильтруются переводы, но не транзакции).
    """
    if allowed_ids is not None and account_id not in allowed_ids:
        return
    day_ops[day][account_id] += delta


def build_day_ops(
    account_ids: list[int],
    transactions: list[Transaction],
    transfers: list[Transfer],
) -> dict[date, dict[int, Decimal]]:
    """
    Раскладывает операции по дням: day_ops[day][acc_id] = дельта.
    """
    account_ids = set(account_ids)
    day_ops: dict[date, dict[int, Decimal]] = defaultdict(lambda: defaultdict(Decimal))

    for tx in transactions:
        day, amount = _extract_day_and_amount(tx, "create_at")
        delta = amount if tx["category__type_transaction"] == "income" else -amount
        _apply_delta(day_ops, day, tx["account_id"], delta)

    for tr in transfers:
        day, amount = _extract_day_and_amount(tr, "timestamp")
        _apply_delta(day_ops, day, tr["source_account_id"], -amount, account_ids)
        _apply_delta(day_ops, day, tr["destination_account_id"], amount, account_ids)

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
