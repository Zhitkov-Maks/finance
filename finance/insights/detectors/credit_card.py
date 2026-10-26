from datetime import date, timedelta
from decimal import Decimal

from accounts.models import Account

from ..models import Insight
from .base import _alist, _save_insight


async def detect_credit_card_grace_for_user(user, today=None) -> int:
    today = today or date.today()

    cards = await _alist(
        Account.objects.filter(
            user=user,
            account_type="credit_card",
            is_active=True,
            balance__lt=0,
            grace_period_start__isnull=False,
        )
    )

    created = 0
    for card in cards:
        end_date = card.grace_period_start + timedelta(days=card.grace_period_days)
        days_left = (end_date - today).days

        # Уведомляем, если осталось 5, 3 или 1 день
        if days_left in (5, 3, 1):
            debt = abs(card.balance)
            # Штраф (например, 30% годовых за 1 день просрочки)
            penalty_rate = Decimal("0.30") / Decimal("365")
            penalty_per_day = debt * penalty_rate

            saved = await _save_insight(
                user=user,
                insight_type=Insight.TYPE_CREDIT_CARD_GRACE,
                severity=Insight.SEVERITY_CRITICAL,
                title=f"⏳ Льготный период по карте «{card.name}»",
                message=(
                    f"Осталось {days_left} дн. до конца беспроцентного периода. "
                    f"Долг: {debt:.0f} ₽. Если не погасить, переплата составит "
                    f"около {penalty_per_day:.0f} ₽ в день."
                ),
                data={
                    "account_id": card.id,
                    "days_left": days_left,
                    "debt": float(debt),
                },
                action_url="/accounts",
                period_key=f"credit_card_grace:{card.id}:{today}",
            )
            if saved:
                created += 1
    return created
