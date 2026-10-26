from datetime import date, timedelta

from accounts.models import Account
from django.db.models import Sum
from recurring.models import RecurringTransaction

from ..models import Insight
from .base import _aaggregate, _alist, _save_insight, _to_decimal


async def detect_cash_gaps_for_user(user, today=None) -> int:
    today = today or date.today()
    lookahead = today + timedelta(days=14)  # Смотрим на 2 недели вперед

    # 1. Свободные деньги (обычные счета и вклады, без кредиток)
    balance_res = await _aaggregate(
        Account.objects.filter(
            user=user, is_active=True, account_type__in=["standard", "deposit"]
        ),
        total=Sum("balance"),
    )
    total_balance = _to_decimal(balance_res["total"])

    # 2. Предстоящие обязательные платежи
    upcoming = await _alist(
        RecurringTransaction.objects.filter(
            user=user,
            is_active=True,
            type_transaction="expense",
            next_run_date__gte=today,
            next_run_date__lte=lookahead,
        )
    )

    if not upcoming:
        return 0

    upcoming_sum = sum(r.amount for r in upcoming)

    if total_balance < upcoming_sum:
        saved = await _save_insight(
            user=user,
            insight_type=Insight.TYPE_CASH_GAP,
            severity=Insight.SEVERITY_CRITICAL,
            title="Кассовый разрыв!",
            message=(
                f"У вас на счетах {total_balance:.0f} ₽, а в ближайшие 14 дней "
                f"нужно оплатить регулярные платежи на {upcoming_sum:.0f} ₽. "
                f"Не хватает {abs(total_balance - upcoming_sum):.0f} ₽."
            ),
            data={
                "total_balance": float(total_balance),
                "upcoming_sum": float(upcoming_sum),
                "shortage": float(abs(total_balance - upcoming_sum)),
            },
            action_url="/recurring",
            period_key=f"cash_gap:{user.id}:{today}",
        )
        return 1 if saved else 0
    return 0
