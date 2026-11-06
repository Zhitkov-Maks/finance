import logging
from datetime import timedelta
from decimal import Decimal

from accounts.models import Account
from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.db.models import Case, DecimalField, Min, Sum, When
from django.utils import timezone
from recurring.models import RecurringTransaction
from transactions.models import Transaction

logger = logging.getLogger(__name__)

CACHE_TTL = 60 * 60 * 24 * 7  # Неделя


class ForecastService:
    def __init__(self, user):
        self.user = user
        self.today = timezone.localdate()
        self.start_of_month = self.today.replace(day=1)
        self.end_of_month = (
            self.start_of_month + relativedelta(months=1) - timedelta(days=1)
        )
        self.days_left = (self.end_of_month - self.today).days + 1

    def calculate(self) -> dict:
        # 1. Проверяем кэш
        cache_key = f"forecast:{self.user.id}:{self.today.isoformat()}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        # 2. Считаем (3 запроса к БД)
        current_balance = self._get_liquid_balance()
        tx_stats = self._get_transaction_stats()
        recurring_stats = self._get_recurring_stats()

        # 3. Высчитываем доходы и расходы из полученной статистики
        expected_income = self._calculate_income(tx_stats, recurring_stats)
        obligatory_expenses = recurring_stats["rec_expense_this_month"]
        variable_expenses = self._calculate_variable_expenses(tx_stats, recurring_stats)

        # 4. Итоги
        guaranteed_balance = current_balance + expected_income - obligatory_expenses
        expected_balance = guaranteed_balance - variable_expenses

        result = {
            "current_balance": float(current_balance),
            "expected_income": float(expected_income),
            "obligatory_expenses": float(obligatory_expenses),
            "variable_expenses": float(variable_expenses),
            "guaranteed_balance": float(guaranteed_balance),
            "expected_balance": float(expected_balance),
            "days_left": self.days_left,
            "period": {
                "date_from": self.today.isoformat(),
                "date_to": self.end_of_month.isoformat(),
            },
        }

        # 5. Сохраняем в кэш
        cache.set(cache_key, result, timeout=CACHE_TTL)
        return result

    def _get_liquid_balance(self) -> Decimal:
        return Account.objects.filter(user=self.user, is_active=True).exclude(
            account_type=Account.TYPE_CREDIT
        ).aggregate(total=Sum("balance"))["total"] or Decimal("0.00")

    def _get_transaction_stats(self) -> dict:
        """Один запрос к БД вместо четырех."""
        six_months_ago = self.today - relativedelta(months=6)
        thirty_days_ago = self.today - timedelta(days=30)

        # Условная агрегация: считаем все суммы за разные периоды в одном SQL-запросе
        return Transaction.objects.filter(user=self.user).aggregate(
            # Доходы за 6 месяцев (без текущего месяца)
            past_income=Sum(
                Case(
                    When(
                        type_transaction=Transaction.TYPE_INCOME,
                        create_at__date__gte=six_months_ago,
                        create_at__date__lt=self.start_of_month,
                        then="amount",
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            # Дата первой транзакции за 6 месяцев (для подсчета месяцев)
            past_min_date=Min(
                Case(
                    When(
                        type_transaction=Transaction.TYPE_INCOME,
                        create_at__date__gte=six_months_ago,
                        create_at__date__lt=self.start_of_month,
                        then="create_at",
                    )
                )
            ),
            # Доходы за текущий месяц
            current_income=Sum(
                Case(
                    When(
                        type_transaction=Transaction.TYPE_INCOME,
                        create_at__date__gte=self.start_of_month,
                        create_at__date__lte=self.today,
                        then="amount",
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            # Переменные расходы за 30 дней
            past_30d_expense=Sum(
                Case(
                    When(
                        type_transaction=Transaction.TYPE_EXPENSE,
                        create_at__date__gte=thirty_days_ago,
                        create_at__date__lte=self.today,
                        then="amount",
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
        )

    def _get_recurring_stats(self) -> dict:
        """Один запрос к БД для всех регулярных операций."""
        next_30_days = self.today + timedelta(days=30)

        return RecurringTransaction.objects.filter(
            user=self.user, is_active=True
        ).aggregate(
            # Доходы до конца месяца
            rec_income_this_month=Sum(
                Case(
                    When(
                        type_transaction=RecurringTransaction.TYPE_INCOME,
                        next_run_date__gte=self.today,
                        next_run_date__lte=self.end_of_month,
                        then="amount",
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            # Обязательные расходы до конца месяца
            rec_expense_this_month=Sum(
                Case(
                    When(
                        type_transaction=RecurringTransaction.TYPE_EXPENSE,
                        next_run_date__gte=self.today,
                        next_run_date__lte=self.end_of_month,
                        then="amount",
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            # Регулярные расходы на ближайшие 30 дней (для вычета из переменных)
            rec_expense_30d=Sum(
                Case(
                    When(
                        type_transaction=RecurringTransaction.TYPE_EXPENSE,
                        next_run_date__gte=self.today,
                        next_run_date__lte=next_30_days,
                        then="amount",
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
        )

    def _calculate_income(self, tx_stats: dict, recurring_stats: dict) -> Decimal:
        rec_income = recurring_stats["rec_income_this_month"] or Decimal("0.00")
        if rec_income > 0:
            return rec_income

        total_past = tx_stats["past_income"] or Decimal("0.00")
        first_date = tx_stats["past_min_date"]

        if total_past > 0 and first_date:
            first_month = first_date.date().replace(day=1)
            delta = relativedelta(self.start_of_month, first_month)
            months_passed = max(1, delta.years * 12 + delta.months)
            avg_monthly_income = total_past / Decimal(months_passed)
        else:
            avg_monthly_income = Decimal("0.00")

        current_month_income = tx_stats["current_income"] or Decimal("0.00")
        expected = avg_monthly_income - current_month_income
        return max(Decimal("0.00"), expected)

    def _calculate_variable_expenses(
        self, tx_stats: dict, recurring_stats: dict
    ) -> Decimal:
        total_30d_expenses = tx_stats["past_30d_expense"] or Decimal("0.00")
        recurring_30d = recurring_stats["rec_expense_30d"] or Decimal("0.00")

        pure_variable_30d = max(Decimal("0.00"), total_30d_expenses - recurring_30d)
        daily_variable = pure_variable_30d / Decimal("30.0")
        return daily_variable * Decimal(self.days_left)
