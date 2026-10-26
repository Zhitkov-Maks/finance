from datetime import date, timedelta
from decimal import Decimal

from accounts.models import Account
from asgiref.sync import sync_to_async
from budgets.models import Budget
from django.db.models import Sum
from transactions.models import Transaction

from ..models import Insight, InsightSettings
from .base import _aaggregate, _alist, _save_insight, _to_decimal


async def detect_idle_cash_for_user(user, today=None) -> int:
    today = today or date.today()

    # Получаем порог
    settings_obj, _ = await sync_to_async(InsightSettings.objects.get_or_create)(
        user=user
    )
    threshold = settings_obj.idle_cash_threshold

    # Считаем баланс обычных счетов
    standard_bal = await _aaggregate(
        Account.objects.filter(user=user, is_active=True, account_type="standard"),
        total=Sum("balance"),
    )
    standard_sum = _to_decimal(standard_bal["total"])

    # Считаем баланс вкладов
    deposit_bal = await _aaggregate(
        Account.objects.filter(user=user, is_active=True, account_type="deposit"),
        total=Sum("balance"),
    )
    deposit_sum = _to_decimal(deposit_bal["total"])

    # Если на обычных счетах много денег, а на вкладах пусто
    if standard_sum >= threshold and deposit_sum == 0:
        potential_income = standard_sum * Decimal("0.1")  # Условно 10% годовых
        saved = await _save_insight(
            user=user,
            insight_type=Insight.TYPE_IDLE_CASH,
            severity=Insight.SEVERITY_INFO,
            title="💰 Деньги должны работать",
            message=(
                f"У вас на счетах лежит {standard_sum:.0f} ₽, но нет вкладов. "
                f"Если открыть вклад под 12%, вы могли бы зарабатывать "
                f"около {potential_income:.0f} ₽ в год."
            ),
            data={
                "standard_sum": float(standard_sum),
                "potential_income": float(potential_income),
            },
            action_url="/accounts",
            period_key=f"idle_cash:{user.id}:{today.strftime('%Y-%m')}",
        )
        return 1 if saved else 0
    return 0


# ==========================================
# 2. Долг дороже вклада
# ==========================================
async def detect_debt_vs_deposit_for_user(user, today=None) -> int:
    # Ищем кредитки с долгом
    cards = await _alist(
        Account.objects.filter(
            user=user, is_active=True, account_type="credit_card", balance__lt=0
        )
    )
    if not cards:
        return 0

    # Ищем вклады
    deposits = await _alist(
        Account.objects.filter(
            user=user, is_active=True, account_type="deposit", balance__gt=0
        )
    )
    if not deposits:
        return 0

    # Берем максимальную ставку по вкладу
    best_deposit_rate = max((d.interest_rate or 0 for d in deposits), default=0)
    # Штраф по кредитке (условно 30%, берем из логики tasks.py)
    penalty_rate = Decimal("30.0")

    # Если штраф больше ставки по вкладу — платить долг выгоднее
    if penalty_rate > best_deposit_rate:
        # Берем самый большой долг
        worst_card = min(cards, key=lambda c: c.balance)
        debt = abs(worst_card.balance)
        # Берем вклад с максимальной суммой
        best_deposit = max(deposits, key=lambda d: d.balance)

        if best_deposit.balance > 0:
            saved = await _save_insight(
                user=user,
                insight_type=Insight.TYPE_DEBT_VS_DEPOSIT,
                severity=Insight.SEVERITY_WARNING,
                title="🚨 Кредит дороже вклада",
                message=(
                    f"Вы платите по кредитке «{worst_card.name}» около {penalty_rate:.0f}% годовых, "
                    f"а ваш вклад «{best_deposit.name}» приносит лишь {best_deposit_rate:.1f}%. "
                    f"Подумайте о том, чтобы погасить часть долга ({debt:.0f} ₽) с вклада."
                ),
                data={
                    "debt": float(debt),
                    "deposit_balance": float(best_deposit.balance),
                },
                action_url="/accounts",
                period_key=f"debt_vs_deposit:{worst_card.id}:{today.strftime('%Y-%m')}",
            )
            return 1 if saved else 0
    return 0


# ==========================================
# 3. Можно отложить (Бюджет)
# ==========================================
async def detect_budget_reallocation_for_user(user, today=None) -> int:
    today = today or date.today()

    # Проверяем только в последние 3 дня месяца
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    days_left = (next_month - today).days
    if days_left > 3 or days_left == 0:
        return 0

    budgets = await _alist(
        Budget.objects.filter(user=user, is_active=True, period_type="monthly")
    )
    if not budgets:
        return 0

    month_start = today.replace(day=1)

    created = 0
    for b in budgets:
        if not b.category_id:  # Пропускаем общий бюджет, смотрим только категории
            continue

        spent = await _aaggregate(
            Transaction.objects.filter(
                user=user,
                category=b.category,
                category__type_transaction="expense",
                create_at__date__gte=month_start,
                create_at__date__lte=today,
            ),
            total=Sum("amount"),
        )
        spent_val = _to_decimal(spent["total"])
        remaining = b.amount - spent_val

        # Если осталось больше 20% и до конца месяца 3 дня
        if remaining > (b.amount * Decimal("0.2")):
            saved = await _save_insight(
                user=user,
                insight_type=Insight.TYPE_BUDGET_REALLOCATION,
                severity=Insight.SEVERITY_INFO,
                title=f"🐷 Можно отложить: {b.category.name}",
                message=(
                    f"По бюджету «{b.category.name}» осталось {remaining:.0f} ₽, "
                    f"а до конца месяца всего {days_left} дн. Переложите остаток в копилку!"
                ),
                data={"budget_id": b.id, "remaining": float(remaining)},
                action_url="/budgets",
                period_key=f"budget_realloc:{b.id}:{today.strftime('%Y-%m')}",
            )
            if saved:
                created += 1

    return created
