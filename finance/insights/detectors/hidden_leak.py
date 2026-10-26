from datetime import date
from decimal import Decimal

from asgiref.sync import sync_to_async
from django.db.models import Case, DecimalField, Sum, Value, When
from transactions.models import Transaction

from ..models import Insight, InsightSettings
from .base import _aaggregate, _save_insight, _to_decimal

LEAK_MIN_TOTAL_EXPENSE = Decimal("3000")


async def _fetch_month_expense_stats(
    user, month_start: date, today: date, threshold
) -> tuple[Decimal, Decimal]:
    result = await _aaggregate(
        Transaction.objects.filter(
            user=user,
            category__type_transaction="expense",
            create_at__date__gte=month_start,
            create_at__date__lte=today,
        ),
        total=Sum("amount"),
        small=Sum(
            Case(
                When(amount__lt=threshold, then="amount"),
                default=Value(0),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        ),
    )
    return _to_decimal(result["total"]), _to_decimal(result["small"])


async def detect_hidden_leaks_for_user(user, today=None) -> int:
    today = today or date.today()
    month_start = today.replace(day=1)

    # Получаем настройки (если нет — создадутся с дефолтами)
    settings_obj, _ = await sync_to_async(InsightSettings.objects.get_or_create)(
        user=user
    )
    threshold = settings_obj.small_expense_threshold

    total_expense, small_expenses = await _fetch_month_expense_stats(
        user, month_start, today, threshold
    )

    if total_expense < LEAK_MIN_TOTAL_EXPENSE:
        return 0

    percent = float(small_expenses) / float(total_expense)
    percent_display = round(percent * 100, 1)
    month_key = today.strftime("%Y-%m")

    # --- ЛОГИКА УРОВНЕЙ (Кнут и пряник) ---
    if percent_display < 5:
        title = "🏆 Вы отлично контролируете мелкие траты!"
        message = (
            f"Мелкие покупки (до {SMALL_EXPENSE_THRESHOLD:.0f} ₽) составили всего "
            f"{percent_display}% от ваших расходов "
            f"({small_expenses:.0f} ₽). Так держать!"
        )
        severity = Insight.SEVERITY_INFO
    elif percent_display <= 10:
        title = "📊 Статистика мелких трат"
        message = (
            f"Мелкие покупки (до {SMALL_EXPENSE_THRESHOLD:.0f} ₽) составили "
            f"{percent_display}% от ваших расходов ({small_expenses:.0f} ₽). "
            f"Всё в пределах нормы."
        )
        severity = Insight.SEVERITY_INFO
    else:
        title = "⚠️ Скрытая утечка бюджета"
        message = (
            f"В этом месяце вы потратили {small_expenses:.0f} ₽ на мелкие покупки. "
            f"Это {percent_display}% от всех расходов! "
            f"Обратите внимание на них."
        )
        severity = Insight.SEVERITY_WARNING

    # Добавляем день в period_key (запускаем раз в 10 дней: 1, 11, 21)
    period_key = f"hidden_leak:{user.id}:{month_key}:{today.day}"

    saved = await _save_insight(
        user=user,
        insight_type=Insight.TYPE_HIDDEN_LEAK,
        severity=severity,
        title=title,
        message=message,
        data={
            "small_expenses": float(small_expenses),
            "total_expense": float(total_expense),
            "percent": percent_display,
            "month": month_key,
        },
        action_url=f"/transactions?create_at_after={month_start}"
        f"&create_at_before={today}&amount_lte={SMALL_EXPENSE_THRESHOLD}",
        period_key=period_key,
    )
    return 1 if saved else 0
