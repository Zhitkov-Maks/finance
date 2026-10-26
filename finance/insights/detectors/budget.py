import calendar
from datetime import date

from budgets.models import Budget
from transactions.models import Transaction

from ..models import Insight
from .base import _aaggregate, _save_insight, _to_decimal


async def detect_budget_overspends_for_user(user, today=None) -> int:
    today = today or date.today()
    month_start = today.replace(day=1)
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_passed = today.day
    days_left = days_in_month - days_passed

    if days_passed < 3:
        return 0

    # Берем общий бюджет на месяц (где category=None)
    budget = await Budget.objects.filter(
        user=user, period_type="monthly", category__isnull=True
    ).afirst()
    if not budget or budget.amount <= 0:
        return 0

    spent_res = await _aaggregate(
        Transaction.objects.filter(
            user=user,
            category__type_transaction="expense",
            create_at__date__gte=month_start,
            create_at__date__lte=today,
        ),
        total=Transaction.objects.model.objects.none().aggregate,
    )
    from django.db.models import Sum

    spent_res = await _aaggregate(
        Transaction.objects.filter(
            user=user,
            category__type_transaction="expense",
            create_at__date__gte=month_start,
            create_at__date__lte=today,
        ),
        total=Sum("amount"),
    )
    spent = _to_decimal(spent_res["total"])

    if spent <= 0:
        return 0

    daily_rate = spent / days_passed
    if daily_rate <= 0:
        return 0

    days_to_exhaust = int((budget.amount - spent) / daily_rate)

    if days_to_exhaust < days_left:
        # Инсайт сработает 1 раз в день
        saved = await _save_insight(
            user=user,
            insight_type=Insight.TYPE_BUDGET_OVERSPEND,
            severity=Insight.SEVERITY_WARNING,
            title="Бюджет под угрозой",
            message=(
                f"При текущем темпе трат ваш бюджет закончится "
                f"через {max(0, days_to_exhaust)} дн. "
                f"До конца месяца осталось {days_left} дн."
            ),
            data={
                "budget_id": budget.id,
                "limit": float(budget.amount),
                "spent": float(spent),
                "days_to_exhaust": max(0, days_to_exhaust),
                "days_left": days_left,
            },
            action_url="/budgets",
            period_key=f"budget_overspend:{budget.id}:{today}",
        )
        return 1 if saved else 0
    return 0
