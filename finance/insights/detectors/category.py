import statistics
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncDate
from transactions.models import Transaction

from ..models import Insight
from .base import _alist, _save_insight

# Пороги
SPIKE_MULTIPLIER = Decimal("2.5")
SPIKE_MIN_DAYS = 5
SPIKE_LOOKBACK_DAYS = 30


async def _fetch_category_spike_data(
    user, period_start: date, today: date
) -> dict[int, dict]:
    qs = (
        Transaction.objects.filter(
            user=user,
            category__type_transaction="expense",
            create_at__date__gte=period_start,
            create_at__date__lte=today,
        )
        .annotate(day=TruncDate("create_at"))
        .values("category_id", "category__name", "day")
        .annotate(total=Sum("amount"))
    )

    grouped: dict[int, dict] = {}
    rows = await _alist(qs)

    for row in rows:
        cat_id = row["category_id"]
        bucket = grouped.setdefault(
            cat_id,
            {"name": row["category__name"], "today_total": Decimal("0"), "daily": []},
        )
        total = row["total"]
        if total is None or total <= 0:
            continue
        if row["day"] == today:
            bucket["today_total"] += total
        else:
            bucket["daily"].append(float(total))
    return grouped


def _spike_metrics(today_total: Decimal, daily_totals: list[float]) -> dict | None:
    if len(daily_totals) < SPIKE_MIN_DAYS:
        return None
    median = statistics.median(daily_totals)
    if median <= 0:
        return None
    if today_total <= Decimal(str(median)) * SPIKE_MULTIPLIER:
        return None
    return {"median": median, "ratio": float(today_total) / median}


async def detect_category_spikes_for_user(user, today=None) -> int:
    today = today or date.today()
    period_start = today - timedelta(days=SPIKE_LOOKBACK_DAYS)

    grouped = await _fetch_category_spike_data(user, period_start, today)
    if not grouped:
        return 0

    created = 0
    for cat_id, bucket in grouped.items():
        today_total = bucket["today_total"]
        if today_total <= 0:
            continue
        metrics = _spike_metrics(today_total, bucket["daily"])
        if metrics is None:
            continue

        category_name = bucket["name"]
        saved = await _save_insight(
            user=user,
            insight_type=Insight.TYPE_CATEGORY_SPIKE,
            severity=Insight.SEVERITY_WARNING,
            title=f"Скачок трат: {category_name}",
            message=(
                f"Сегодня в категории «{category_name}» потрачено "
                f"{today_total:.0f} ₽ — это в {metrics['ratio']:.1f}× больше обычного "
                f"(медиана {metrics['median']:.0f} ₽/день)."
            ),
            data={
                "category_id": cat_id,
                "category_name": category_name,
                "today_total": float(today_total),
                "median_daily": metrics["median"],
                "ratio": round(metrics["ratio"], 2),
                "for_date": str(today),
            },
            action_url=(
                f"/transactions?category_name={category_name}"
                f"&create_at_after={today}&create_at_before={today}"
            ),
            period_key=f"category_spike:{cat_id}:{today}",
        )
        if saved:
            created += 1
    return created
