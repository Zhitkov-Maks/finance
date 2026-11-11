import logging
from datetime import timedelta
from decimal import Decimal

from accounts.models import Account
from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.db.models import Case, DecimalField, Min, Q, Sum, When
from django.utils import timezone
from recurring.models import RecurringTransaction
from transactions.models import Transaction

logger = logging.getLogger(__name__)

# Кэш прогноза живёт сутки (ключ включает дату — на следующий день ключ новый)
CACHE_TTL = 60 * 60 * 24  # 24 часа

# Кэш recurring-статистики — с запасом на смену суток и сигналы инвалидации
RECURRING_CACHE_TTL = 60 * 60 * 25  # 25 часов

RECURRING_AUTO_PREFIX = "[Авто]"


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
        cache_key = f"forecast:{self.user.id}:{self.today.isoformat()}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        # 1. Данные из БД (с учётом кэша recurring отдельно)
        current_balance = self._get_liquid_balance()
        tx_stats = self._get_transaction_stats()
        recurring_stats = self._get_recurring_stats()

        # 2. Расчёты
        expected_income = self._calculate_income(tx_stats, recurring_stats)
        obligatory_expenses = recurring_stats["rec_expense_this_month"]
        variable_expenses = self._calculate_variable_expenses(tx_stats)

        guaranteed_balance = current_balance + expected_income - obligatory_expenses
        expected_balance = guaranteed_balance - variable_expenses

        spent_today = tx_stats["today_variable_expense"] or Decimal("0.00")
        safe_daily = (
            guaranteed_balance / Decimal(self.days_left)
            if self.days_left > 0
            else Decimal("0.00")
        )
        remaining_today = max(Decimal("0.00"), safe_daily - spent_today)

        result = {
            "current_balance": float(current_balance),
            "expected_income": float(expected_income),
            "obligatory_expenses": float(obligatory_expenses),
            "variable_expenses": float(variable_expenses),
            "guaranteed_balance": float(guaranteed_balance),
            "expected_balance": float(expected_balance),
            "safe_to_spend_daily": float(safe_daily),
            "spent_today": float(spent_today),
            "recurring_paid_today": float(self._get_recurring_paid_today()),
            "remaining_safe_today": float(remaining_today),
            "days_left": self.days_left,
            "period": {
                "date_from": self.today.isoformat(),
                "date_to": self.end_of_month.isoformat(),
            },
        }

        cache.set(cache_key, result, timeout=CACHE_TTL)
        return result

    def _get_recurring_paid_today(self) -> Decimal:
        """
        Сколько recurring-расходов прошло сегодня
        — для отображения отдельной строкой в UI.
        """
        return Transaction.objects.filter(
            recurring_source__isnull=False,
            user=self.user,
            type_transaction=Transaction.TYPE_EXPENSE,
            create_at__date=self.today,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    def _get_liquid_balance(self) -> Decimal:
        return Account.objects.filter(
            user=self.user,
            is_active=True,
            deleted_at__isnull=True,
        ).exclude(account_type=Account.TYPE_CREDIT).aggregate(total=Sum("balance"))[
            "total"
        ] or Decimal("0.00")

    def _get_transaction_stats(self) -> dict:
        six_months_ago = self.today - relativedelta(months=6)
        thirty_days_ago = self.today - timedelta(days=1) - relativedelta(months=1)

        # Общий фильтр «не recurring» — чтобы не задваивать обязательные платежи
        not_recurring = ~(
            Q(recurring_source__isnull=False)
            | Q(comment__startswith=RECURRING_AUTO_PREFIX)
        )

        return Transaction.objects.filter(user=self.user).aggregate(
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
            current_income=Sum(
                Case(
                    When(
                        type_transaction=Transaction.TYPE_INCOME,
                        create_at__date__gte=self.start_of_month,
                        create_at__date__lt=self.today,
                        then="amount",
                    ),
                    default=0,
                    output_field=DecimalField(),
                )
            ),
            # Только ПЕРЕМЕННЫЕ расходы — recurring учтены отдельно как obligatory
            past_30d_variable_expense=Sum(
                "amount",
                filter=Q(
                    type_transaction=Transaction.TYPE_EXPENSE,
                    create_at__date__gte=thirty_days_ago,
                    create_at__date__lt=self.today,
                )
                & not_recurring,
            ),
            today_variable_expense=Sum(
                "amount",
                filter=Q(
                    type_transaction=Transaction.TYPE_EXPENSE,
                    create_at__date=self.today,
                )
                & not_recurring,
            ),
        )

    def _recurring_cache_key(self) -> str:
        return f"recurring_stats:{self.user.id}:{self.today.isoformat()}"

    def _get_recurring_stats(self) -> dict:
        """
        Считает сумму регулярных доходов/расходов за оставшуюся часть месяца.

        Важно: учитывает ВСЕ вхождения повторяющихся операций в периоде
        [today, end_of_month], а не только ближайшее (next_run_date).
        Ежедневные — N раз, еженедельные — ~4, ежемесячные — 1.

        Кэшируется отдельно от forecast-кэша:
        - НЕ сбрасывается на транзакции (recurring от них не зависит);
        - сбрасывается сигналом post_save/post_delete на RecurringTransaction;
        - TTL 25 ч — на случай пропущенного сигнала / смены суток.
        """
        cache_key = self._recurring_cache_key()
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        rec_income = Decimal("0")
        rec_expense = Decimal("0")

        qs = RecurringTransaction.objects.filter(
            user=self.user,
            is_active=True,
        )

        for rec in qs:
            if rec.next_run_date is None:
                continue

            curr = max(rec.next_run_date, self.today)
            max_date = (
                min(self.end_of_month, rec.end_date)
                if rec.end_date
                else self.end_of_month
            )

            while curr <= max_date:
                if rec.type_transaction == RecurringTransaction.TYPE_INCOME:
                    rec_income += rec.amount
                else:
                    rec_expense += rec.amount

                next_curr = rec.calculate_next_run(curr)
                if next_curr <= curr:
                    logger.warning(
                        "RecurringTransaction id=%s calculate_next_run "
                        "returned non-increasing date (%s -> %s). Aborting loop.",
                        rec.id,
                        curr,
                        next_curr,
                    )
                    break
                curr = next_curr

        result = {
            "rec_income_this_month": rec_income,
            "rec_expense_this_month": rec_expense,
        }
        cache.set(cache_key, result, timeout=RECURRING_CACHE_TTL)
        return result

    def _calculate_income(self, tx_stats: dict, recurring_stats: dict) -> Decimal:
        """
        Прогноз дохода до конца месяца:
        1. Если есть регулярный доход — берём сумму оставшихся вхождений.
        2. Иначе — средний доход за прошлые месяцы минус уже полученный в этом.
        """
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

    def _calculate_variable_expenses(self, tx_stats: dict) -> Decimal:
        """
        Прогноз переменных расходов до конца месяца.
        Recurring здесь не участвуют — они уже в obligatory_expenses.
        """
        pure_variable_30d = tx_stats["past_30d_variable_expense"] or Decimal("0.00")
        daily_variable = pure_variable_30d / Decimal("30.0")
        return daily_variable * Decimal(self.days_left)
