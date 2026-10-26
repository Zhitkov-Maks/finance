from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Case, DecimalField, Sum, When
from transactions.models import Transaction

from ..models import Insight
from .base import _aaggregate, _save_insight, _to_decimal

# Минимальный прирост нормы сбережений для срабатывания (5%)
IMPROVEMENT_THRESHOLD = Decimal("0.05")


async def detect_savings_improved_for_user(user, today=None) -> int:
    today = today or date.today()

    # Не запускаем в начале месяца, чтобы не сравнивать 2 дня с полным прошлым месяцем
    if today.day < 7:
        return 0

    month_start = today.replace(day=1)
    prev_month_end = month_start - timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)

    # 1. Считаем текущий месяц (с 1-го числа по сегодня)
    curr_stats = await _aaggregate(
        Transaction.objects.filter(
            user=user, create_at__date__gte=month_start, create_at__date__lte=today
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
    curr_income = _to_decimal(curr_stats["income"])
    curr_expense = _to_decimal(curr_stats["expense"])

    # Если доходов еще не было, нет смысла считать процент
    if curr_income <= 0:
        return 0

    # 2. Считаем прошлый месяц (полный)
    prev_stats = await _aaggregate(
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
    prev_income = _to_decimal(prev_stats["income"])
    prev_expense = _to_decimal(prev_stats["expense"])

    if prev_income <= 0:
        return 0

    # 3. Считаем норму сбережений (Savings Rate)
    # Формула: (Доходы - Расходы) / Доходы
    curr_rate = (curr_income - curr_expense) / curr_income
    prev_rate = (prev_income - prev_expense) / prev_income

    improvement = curr_rate - prev_rate

    # 4. Если улучшение существенное (>= 5%)
    if improvement >= IMPROVEMENT_THRESHOLD:
        percent_curr = round(float(curr_rate) * 100)
        percent_prev = round(float(prev_rate) * 100)

        # Красиво форматируем текст, если ушли в минус или вышли из него
        if percent_curr < 0:
            message = (
                f"В этом месяце вы пока тратите больше, чем зарабатываете ({percent_curr}%). "
                f"Но это всё равно лучше, чем в прошлом месяце ({percent_prev}%). Продолжайте!"
            )
        else:
            message = (
                f"В этом месяце вы сэкономили {percent_curr}% дохода, "
                f"а в прошлом — {percent_prev}%. Так держать!"
            )

        saved = await _save_insight(
            user=user,
            insight_type=Insight.TYPE_SAVINGS_IMPROVED,
            severity=Insight.SEVERITY_INFO,
            title="📈 Вы стали больше экономить!",
            message=message,
            data={
                "current_rate": percent_curr,
                "prev_rate": percent_prev,
                "improvement": round(float(improvement) * 100, 1),
            },
            action_url="/statistics",
            period_key=f"savings_improved:{user.id}:{month_start.strftime('%Y-%m')}",
        )
        return 1 if saved else 0

    return 0
