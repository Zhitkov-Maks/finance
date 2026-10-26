from datetime import date

from accounts.models import Account

from ..models import Insight
from .base import _alist, _save_insight


async def detect_deposit_forecasts_for_user(user, today=None) -> int:
    today = today or date.today()
    # Запускать раз в месяц (1 числа)
    if today.day != 1:
        return 0

    deposits = await _alist(
        Account.objects.filter(
            user=user,
            account_type="deposit",
            is_active=True,
            balance__gt=0,
            interest_rate__gt=0,
        )
    )

    created = 0
    for dep in deposits:
        P = float(dep.balance)
        r = float(dep.interest_rate) / 100
        # Сложный процент, ежедневная капитализация
        future_value = P * ((1 + r / 365) ** 365)
        profit = future_value - P

        saved = await _save_insight(
            user=user,
            insight_type=Insight.TYPE_DEPOSIT_FORECAST,
            severity=Insight.SEVERITY_INFO,
            title=f"📈 Прогноз по вкладу «{dep.name}»",
            message=(
                f"Если не снимать деньги, через год на вашем счете будет "
                f"{future_value:.0f} ₽. Чистая прибыль составит {profit:.0f} ₽."
            ),
            data={
                "account_id": dep.id,
                "current": P,
                "future": future_value,
                "profit": profit,
            },
            action_url="/accounts",
            period_key=f"deposit_forecast:{dep.id}:{today.strftime('%Y-%m')}",
        )
        if saved:
            created += 1
    return created
