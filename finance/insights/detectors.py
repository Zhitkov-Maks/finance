import logging
import statistics
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncDate
from transactions.models import Transaction

from .models import Insight
from .services import create_insight

logger = logging.getLogger(__name__)


# === Детектор 1: Скачок в категории ===

SPIKE_MULTIPLIER = Decimal("2.5")  # во сколько раз больше медианы = алерт
SPIKE_MIN_DAYS = 5  # мин. кол-во дней для расчёта медианы
SPIKE_LOOKBACK_DAYS = 30  # окно для расчёта


def detect_category_spikes_for_user(user, today=None) -> int:
    """
    Ищет сегодняшние траты по категориям, которые больше медианы
    дневных трат за последние 30 дней в SPIKE_MULTIPLIER раз.
    """
    if today is None:
        today = date.today()

    period_start = today - timedelta(days=SPIKE_LOOKBACK_DAYS)
    period_end = today - timedelta(days=1)

    today_by_category = (
        Transaction.objects.filter(
            user=user,
            create_at__date=today,
            category__type_transaction="expense",
        )
        .values("category_id", "category__name")
        .annotate(total=Sum("amount"))
    )

    if not today_by_category:
        return 0

    created = 0
    for row in today_by_category:
        category_id = row["category_id"]
        today_total = row["total"] or Decimal(0)
        category_name = row["category__name"]

        if today_total <= 0:
            continue

        daily = (
            Transaction.objects.filter(
                user=user,
                category_id=category_id,
                category__type_transaction="expense",
                create_at__date__gte=period_start,
                create_at__date__lte=period_end,
            )
            .annotate(day=TruncDate("create_at"))
            .values("day")
            .annotate(total=Sum("amount"))
        )

        daily_totals = [
            float(d["total"] or 0) for d in daily if d["total"] and d["total"] > 0
        ]

        if len(daily_totals) < SPIKE_MIN_DAYS:
            continue

        median = statistics.median(daily_totals)
        if median <= 0:
            continue

        threshold = Decimal(str(median)) * SPIKE_MULTIPLIER
        if today_total > threshold:
            ratio = float(today_total) / median
            created_flag = create_insight(
                user=user,
                insight_type=Insight.TYPE_CATEGORY_SPIKE,
                severity=Insight.SEVERITY_WARNING,
                title=f"Скачок трат: {category_name}",
                message=(
                    f"Сегодня в категории «{category_name}» потрачено "
                    f"{today_total:.0f} ₽ — это в {ratio:.1f}× больше обычного "
                    f"(медиана {median:.0f} ₽/день)."
                ),
                data={
                    "category_id": category_id,
                    "category_name": category_name,
                    "today_total": float(today_total),
                    "median_daily": median,
                    "ratio": round(ratio, 2),
                    "for_date": str(today),
                },
                action_url=(
                    f"/transactions?category_name={category_name}"
                    f"&create_at_after={today}&create_at_before={today}"
                ),
                period_key=f"category_spike:{category_id}:{today}",
            )
            if created_flag:
                created += 1

    return created
