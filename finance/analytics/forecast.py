from datetime import timedelta
from decimal import Decimal

from accounts.models import Account
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.utils import timezone
from recurring.models import RecurringTransaction
from transactions.models import Transaction


class ForecastService:
    def __init__(self, user):
        self.user = user
        self.today = timezone.localdate()
        self.end_of_month = (
            self.today.replace(day=1) + relativedelta(months=1) - timedelta(days=1)
        )
        self.days_left = (self.end_of_month - self.today).days + 1

    def calculate(self) -> dict:
        liquid_accounts = Account.objects.filter(
            user=self.user, is_active=True
        ).exclude(account_type=Account.TYPE_CREDIT)

        current_balance = liquid_accounts.aggregate(total=Sum("balance"))[
            "total"
        ] or Decimal("0.00")

        # 2. Доходы
        expected_income = self._calculate_income()

        # 3. Обязательные расходы (Регулярные операции до конца месяца)
        obligatory_expenses = self._calculate_obligatory_expenses()

        # 4. Переменные расходы (средний расход в день на основе истории)
        variable_expenses = self._calculate_variable_expenses()

        # 5. Итоги
        guaranteed_balance = current_balance + expected_income - obligatory_expenses
        expected_balance = guaranteed_balance - variable_expenses

        return {
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

    def _calculate_income(self) -> Decimal:
        # Ищем регулярные доходы в этом месяце
        recurring_income = RecurringTransaction.objects.filter(
            user=self.user,
            type_transaction=RecurringTransaction.TYPE_INCOME,
            is_active=True,
            next_run_date__gte=self.today,
            next_run_date__lte=self.end_of_month,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        if recurring_income > 0:
            return recurring_income

        # Фоллбэк: если регулярных доходов нет, считаем средний за 6 месяцев
        six_months_ago = self.today - relativedelta(months=6)

        # Доходы за прошлые 6 месяцев (не включая текущий)
        past_incomes = Transaction.objects.filter(
            user=self.user,
            type_transaction=Transaction.TYPE_INCOME,
            create_at__date__gte=six_months_ago,
            create_at__date__lt=self.today.replace(day=1),
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        avg_monthly_income = past_incomes / Decimal("6.0")

        # Уже полученный доход в этом месяце
        current_month_income = Transaction.objects.filter(
            user=self.user,
            type_transaction=Transaction.TYPE_INCOME,
            create_at__date__gte=self.today.replace(day=1),
            create_at__date__lte=self.today,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        # Остаток до среднего
        expected = avg_monthly_income - current_month_income
        return max(Decimal("0.00"), expected)

    def _calculate_obligatory_expenses(self) -> Decimal:
        return RecurringTransaction.objects.filter(
            user=self.user,
            type_transaction=RecurringTransaction.TYPE_EXPENSE,
            is_active=True,
            next_run_date__gte=self.today,
            next_run_date__lte=self.end_of_month,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    def _calculate_variable_expenses(self) -> Decimal:
        # Берем траты за последние 30 дней
        thirty_days_ago = self.today - timedelta(days=30)
        total_30d_expenses = Transaction.objects.filter(
            user=self.user,
            type_transaction=Transaction.TYPE_EXPENSE,
            create_at__date__gte=thirty_days_ago,
            create_at__date__lte=self.today,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        # Аппроксимируем регулярные траты за последние 30 дней,
        # чтобы вычесть их из общей суммы (они уже учтены в балансе или в обязательных)
        next_30_days = self.today + timedelta(days=30)
        recurring_30d = RecurringTransaction.objects.filter(
            user=self.user,
            type_transaction=RecurringTransaction.TYPE_EXPENSE,
            is_active=True,
            next_run_date__gte=self.today,
            next_run_date__lte=next_30_days,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        # Чистые переменные траты за 30 дней
        pure_variable_30d = max(Decimal("0.00"), total_30d_expenses - recurring_30d)

        # Средний в день * оставшиеся дни
        daily_variable = pure_variable_30d / Decimal("30.0")
        return daily_variable * Decimal(self.days_left)
