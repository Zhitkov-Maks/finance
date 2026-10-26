import asyncio
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncDate
from transactions.models import Transaction

from ..models import Insight
from .base import _aaggregate, _alist, _save_insight, _to_decimal

# Пороги
SALARY_THRESHOLD = Decimal("15000")
SALARY_SPIKE_MULTIPLIER = Decimal("2.5")
SALARY_LOOKBACK_DAYS = 7
AVG_LOOKBACK_DAYS = 90


async def _fetch_recent_big_incomes(user, today: date) -> list[dict]:
    qs = (
        Transaction.objects.filter(
            user=user,
            category__type_transaction="income",
            amount__gte=SALARY_THRESHOLD,
            create_at__date__gte=today - timedelta(days=SALARY_LOOKBACK_DAYS),
            create_at__date__lte=today - timedelta(days=1),
        )
        .annotate(day=TruncDate("create_at"))
        .values("id", "amount", "day")
    )
    return await _alist(qs)


async def _get_avg_daily_expense(user, today: date) -> Decimal:
    result = await _aaggregate(
        Transaction.objects.filter(
            user=user,
            category__type_transaction="expense",
            create_at__date__gte=today - timedelta(days=AVG_LOOKBACK_DAYS),
            create_at__date__lt=today,
        ),
        total=Sum("amount"),
    )
    return _to_decimal(result["total"]) / AVG_LOOKBACK_DAYS


async def _fetch_expense_sum_by_dates(
    user, target_dates: set[date]
) -> dict[date, Decimal]:
    if not target_dates:
        return {}
    qs = (
        Transaction.objects.filter(
            user=user,
            category__type_transaction="expense",
            create_at__date__in=target_dates,
        )
        .annotate(day=TruncDate("create_at"))
        .values("day")
        .annotate(total=Sum("amount"))
    )

    result: dict[date, Decimal] = {}
    rows = await _alist(qs)
    for row in rows:
        result[row["day"]] = _to_decimal(row["total"])
    return result


async def detect_salary_spikes_for_user(user, today=None) -> int:
    today = today or date.today()

    incomes = await _fetch_recent_big_incomes(user, today)
    if not incomes:
        return 0

    target_dates: set[date] = set()
    for inc in incomes:
        d = inc["day"]
        target_dates.add(d)
        target_dates.add(d + timedelta(days=1))

    avg_daily_expense, expenses_by_date = await asyncio.gather(
        _get_avg_daily_expense(user, today),
        _fetch_expense_sum_by_dates(user, target_dates),
    )
    if avg_daily_expense <= 0:
        return 0

    created = 0
    for inc in incomes:
        income_date = inc["day"]
        next_date = income_date + timedelta(days=1)
        spent_after = expenses_by_date.get(
            income_date, Decimal("0")
        ) + expenses_by_date.get(next_date, Decimal("0"))
        expected_spent = avg_daily_expense * 2

        if expected_spent <= 0:
            continue
        if spent_after <= expected_spent * SALARY_SPIKE_MULTIPLIER:
            continue

        ratio = float(spent_after) / float(expected_spent)
        saved = await _save_insight(
            user=user,
            insight_type=Insight.TYPE_SALARY_SPIKE,
            severity=Insight.SEVERITY_INFO,
            title="Траты после зарплаты",
            message=(
                f"В день зарплаты и на следующий день вы потратили {spent_after:.0f} ₽. "
                f"Это в {ratio:.1f} раза больше вашей обычной нормы за 2 дня."
            ),
            data={
                "income_id": inc["id"],
                "income_amount": float(inc["amount"]),
                "income_date": str(income_date),
                "spent_after": float(spent_after),
                "expected_spent": float(expected_spent),
                "ratio": round(ratio, 1),
            },
            action_url=f"/transactions?create_at_after={income_date}"
            f"&create_at_before={next_date}",
            period_key=f"salary_spike:{inc['id']}",
        )
        if saved:
            created += 1
    return created
