import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from accounts.models import Account

DEFAULT_CREDIT_RATE = Decimal("30.0")
DEFAULT_MIN_PAYMENT_PERCENT = Decimal("5.0")
MAX_MONTHS_SIMULATION = 120


@dataclass
class CardState:
    """Состояние кредитной карты в процессе симуляции."""

    id: int
    name: str
    balance: Decimal
    initial_balance: Decimal
    rate: Decimal
    min_payment_percent: Decimal
    grace_days_left: int

    total_paid: Decimal = Decimal("0.00")
    total_interest: Decimal = Decimal("0.00")
    month_paid_off: int | None = None
    current_min_pay: Decimal = Decimal("0.00")


class CreditStrategyService:
    def __init__(self, user, monthly_budget: Decimal, strategy: str):
        self.user = user
        self.monthly_budget = monthly_budget
        self.strategy = strategy  # 'avalanche' or 'snowball'
        self.today = date.today()

    def simulate(self) -> dict:
        """Запускает симуляцию и возвращает результат для фронтенда."""
        cards = list(
            Account.objects.filter(
                user=self.user, account_type=Account.TYPE_CREDIT, balance__lt=0
            ).only(
                "id",
                "name",
                "balance",
                "credit_rate",
                "min_payment_percent",
                "grace_period_start",
                "grace_period_days",
            )
        )

        if not cards:
            return {"error": "У вас нет кредитных карт с задолженностью."}

        state_cards = self._prepare_cards(cards)

        schedule = []
        months = 0
        current_date = self.today

        # Основной цикл симуляции (месяц за месяцем)
        while self._has_active_debt(state_cards) and months < MAX_MONTHS_SIMULATION:
            months += 1

            # Вычисляем, сколько дней в текущем симулируемом месяце
            next_date = self._add_months(current_date, 1)
            days_in_month = (next_date - current_date).days

            # 1. Начисление процентов
            month_interest = self._accrue_interest(state_cards, days_in_month)

            # 2. Расчет минимальных платежей
            total_min_payments = self._calculate_min_payments(state_cards)

            # 3. Проверка бюджета
            if self.monthly_budget < total_min_payments:
                return {
                    "error": f"Суммы {self.monthly_budget:.2f} ₽ недостаточно "
                    f"для покрытия минимальных платежей ({total_min_payments:.2f} ₽). "
                    f"Увеличьте бюджет или проверьте проценты "
                    f"минимальных платежей в карточках."
                }

            # 4. Внесение минимальных платежей
            budget_left = self._apply_min_payments(state_cards, months)

            # 5. Распределение оставшегося бюджета (сверх минимума)
            self._apply_extra_payments(state_cards, budget_left, months)

            # 6. Фиксация состояния на конец месяца для графика
            schedule.append(
                {
                    "month": months,
                    "remaining_debt": float(sum(c.balance for c in state_cards)),
                    "interest_paid": float(month_interest),
                }
            )

            current_date = next_date

        return self._build_response(state_cards, schedule, months)

    def _prepare_cards(self, cards) -> list[CardState]:
        """Конвертирует объекты БД в состояние для симуляции."""
        state_cards = []
        for c in cards:
            rate = Decimal(str(c.credit_rate)) if c.credit_rate else DEFAULT_CREDIT_RATE

            # Берем процент из настроек карты, либо дефолтные 5%
            min_pct_val = getattr(c, "min_payment_percent", None)
            min_pct = (
                Decimal(str(min_pct_val))
                if min_pct_val
                else DEFAULT_MIN_PAYMENT_PERCENT
            )

            # Считаем дни льготного периода
            grace_days_left = 0
            if c.grace_period_start and c.grace_period_days:
                end_date = c.grace_period_start + timedelta(days=c.grace_period_days)
                if end_date > self.today:
                    grace_days_left = (end_date - self.today).days

            initial_balance = abs(Decimal(str(c.balance)))

            state_cards.append(
                CardState(
                    id=c.id,
                    name=c.name,
                    balance=initial_balance,
                    initial_balance=initial_balance,
                    rate=rate,
                    min_payment_percent=min_pct,
                    grace_days_left=grace_days_left,
                )
            )
        return state_cards

    def _accrue_interest(
        self, state_cards: list[CardState], days_in_month: int
    ) -> Decimal:
        """
        Начисляет проценты по дням с учетом календарных дней месяца
        и оставшегося льготного периода.
        """
        month_interest = Decimal("0.00")

        for c in state_cards:
            if c.balance <= 0:
                continue

            # Сколько дней месяца попадает под грейс, а сколько - под проценты
            grace_days_this_month = min(days_in_month, c.grace_days_left)
            non_grace_days = days_in_month - grace_days_this_month

            if non_grace_days > 0:
                # Дневная ставка: (Годовая ставка / 100) / 365
                daily_rate = c.rate / Decimal("36500.00")
                interest = c.balance * daily_rate * non_grace_days
                interest = interest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                c.balance += interest
                c.total_interest += interest
                month_interest += interest

            # Уменьшаем оставшийся льготный период
            c.grace_days_left = max(0, c.grace_days_left - days_in_month)

        return month_interest

    def _calculate_min_payments(self, state_cards: list[CardState]) -> Decimal:
        """Рассчитывает минимальные платежи по каждой карте."""
        total_min = Decimal("0.00")

        for c in state_cards:
            if c.balance <= 0:
                c.current_min_pay = Decimal("0.00")
                continue

            min_pay = c.balance * (c.min_payment_percent / Decimal("100.00"))
            min_pay = min_pay.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            # Защита от бесконечного цикла, если баланс копеечный
            min_pay = max(min_pay, Decimal("1.00"))
            # Нельзя списать больше, чем есть на карте
            min_pay = min(min_pay, c.balance)

            c.current_min_pay = min_pay
            total_min += min_pay

        return total_min

    def _apply_min_payments(
        self, state_cards: list[CardState], current_month: int
    ) -> Decimal:
        """Списывает минимальные платежи и возвращает остаток бюджета."""
        budget_left = self.monthly_budget

        for c in state_cards:
            if c.balance <= 0:
                continue

            pay = c.current_min_pay
            c.balance -= pay
            c.total_paid += pay
            budget_left -= pay

            self._check_paid_off(c, current_month)

        return budget_left

    def _apply_extra_payments(
        self, state_cards: list[CardState], budget_left: Decimal, current_month: int
    ):
        """Распределяет остаток бюджета согласно выбранной стратегии."""
        if budget_left <= 0:
            return

        active_cards = [c for c in state_cards if c.balance > 0]

        if self.strategy == "avalanche":
            # Лавина: от самой высокой ставки к низкой. При равенстве — меньший баланс.
            active_cards.sort(key=lambda x: (x.rate, -x.balance), reverse=True)
        else:
            # Снежный ком: от самого маленького баланса к большому.
            # При равенстве — высокая ставка.
            active_cards.sort(key=lambda x: (x.balance, -x.rate))

        for target in active_cards:
            if budget_left <= 0:
                break

            extra_pay = min(target.balance, budget_left)
            target.balance -= extra_pay
            target.total_paid += extra_pay
            budget_left -= extra_pay

            self._check_paid_off(target, current_month)

    def _check_paid_off(self, card: CardState, current_month: int):
        """Проверяет, погашена ли карта полностью."""
        if card.balance <= Decimal("0.01") and card.month_paid_off is None:
            card.balance = Decimal("0.00")
            card.month_paid_off = current_month

    def _has_active_debt(self, state_cards: list[CardState]) -> bool:
        """Проверяет, остались ли еще долги."""
        return any(c.balance > Decimal("0.01") for c in state_cards)

    def _add_months(self, sourcedate: date, months: int) -> date:
        """Прибавляет календарные месяцы к дате с учетом разной длины месяцев."""
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def _build_response(
        self, state_cards: list[CardState], schedule: list[dict], months: int
    ) -> dict:
        """Формирует итоговый JSON-ответ для фронтенда."""
        payoff_order = []
        for c in state_cards:
            if c.month_paid_off is not None:
                # Первоначальный минимальный платеж (для инфо на фронте)
                initial_min = (
                    c.initial_balance * (c.min_payment_percent / Decimal("100.00"))
                ).quantize(Decimal("0.01"))

                payoff_order.append(
                    {
                        "id": c.id,
                        "name": c.name,
                        "balance": float(c.initial_balance),
                        "rate": float(c.rate),
                        "min_payment_percent": float(c.min_payment_percent),
                        "min_payment": float(initial_min),
                        "grace_days_left": c.grace_days_left,
                        "total_paid": float(c.total_paid),
                        "total_interest": float(c.total_interest),
                        "month_paid_off": c.month_paid_off,
                    }
                )

        return {
            "months": months,
            "total_interest": float(sum(c.total_interest for c in state_cards)),
            "total_paid": float(sum(c.total_paid for c in state_cards)),
            "payoff_order": sorted(payoff_order, key=lambda x: x["month_paid_off"]),
            "schedule": schedule,
        }
