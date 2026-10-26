from datetime import date, timedelta

from django.db.models import Sum
from transactions.models import Transaction

from ..models import Insight
from .base import _aaggregate, _alist, _save_insight, _to_decimal


async def detect_monthly_report_for_user(user, today=None) -> int:
    today = today or date.today()
    if today.day != 1:  # Запускаем только 1-го числа
        return 0

    # Берем прошлый месяц
    prev_month_end = today - timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)

    from django.db.models import Case, DecimalField, When

    stats = await _aaggregate(
        Transaction.objects.filter(
            user=user,
            create_at__date__gte=prev_month_start,
            create_at__date__lte=prev_month_end,
        ),
        income=Sum(
            Case(
                When(category__type_transaction="income", then="amount"),
                default=0,
                output_field=DecimalField(),
            )
        ),
        expense=Sum(
            Case(
                When(category__type_transaction="expense", then="amount"),
                default=0,
                output_field=DecimalField(),
            )
        ),
    )
    income = _to_decimal(stats["income"])
    expense = _to_decimal(stats["expense"])

    if income == 0 and expense == 0:
        return 0

    # Топ-3 категории расходов
    top_cats_qs = (
        Transaction.objects.filter(
            user=user,
            category__type_transaction="expense",
            create_at__date__gte=prev_month_start,
            create_at__date__lte=prev_month_end,
        )
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:3]
    )
    top_cats = await _alist(top_cats_qs)
    top_cats_str = ", ".join(
        [f"{c['category__name']} ({c['total']:.0f} ₽)" for c in top_cats]
    )

    month_name = prev_month_start.strftime("%B %Y")

    saved = await _save_insight(
        user=user,
        insight_type=Insight.TYPE_MONTHLY_REPORT,
        severity=Insight.SEVERITY_INFO,
        title=f"📊 Итоги за {month_name}",
        message=(
            f"Доходы: {income:.0f} ₽. Расходы: {expense:.0f} ₽. "
            f"Топ трат: {top_cats_str}."
        ),
        data={
            "income": float(income),
            "expense": float(expense),
            "month": str(prev_month_start),
        },
        action_url="/statistics",
        period_key=f"monthly_report:{user.id}:{prev_month_start.strftime('%Y-%m')}",
    )
    return 1 if saved else 0
