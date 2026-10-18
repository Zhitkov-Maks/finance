from datetime import date, timedelta

from accounts.models import Account
from app_user.models import CustomUser
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db import models
from transactions.models import Category


class RecurringTransaction(models.Model):
    """
    Шаблон регулярной операции (подписка, зарплата, аренда).
    Celery раз в день проверяет next_run_date и создает реальную транзакцию.
    """

    TYPE_INCOME = "income"
    TYPE_EXPENSE = "expense"
    TYPE_CHOICES = [
        (TYPE_INCOME, "Доход"),
        (TYPE_EXPENSE, "Расход"),
    ]

    SCHEDULE_DAILY = "daily"
    SCHEDULE_WEEKLY = "weekly"
    SCHEDULE_MONTHLY = "monthly"
    SCHEDULE_CHOICES = [
        (SCHEDULE_DAILY, "Ежедневно"),
        (SCHEDULE_WEEKLY, "Еженедельно"),
        (SCHEDULE_MONTHLY, "Ежемесячно"),
    ]

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="recurring_transactions"
    )
    title = models.CharField(
        max_length=255, help_text="Например: Netflix, Зарплата, Аренда"
    )
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="recurring_transactions"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="recurring_transactions"
    )
    type_transaction = models.CharField(max_length=10, choices=TYPE_CHOICES)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.TextField(blank=True, default="")

    schedule_type = models.CharField(
        max_length=10, choices=SCHEDULE_CHOICES, default=SCHEDULE_MONTHLY
    )
    day_of_month = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Для месячных (1-31)"
    )
    weekday = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Для недельных (0 - Пн, 6 - Вс)"
    )

    start_date = models.DateField(default=date.today)
    end_date = models.DateField(
        null=True, blank=True, help_text="Если пусто — бессрочно"
    )

    next_run_date = models.DateField()
    last_run_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["next_run_date", "title"]
        verbose_name = "Регулярная операция"
        verbose_name_plural = "Регулярные операции"

    def __str__(self):
        return f"{self.title} ({self.amount} ₽) — {self.get_schedule_type_display()}"

    def clean(self):
        if self.category.user_id != self.user_id:
            raise ValidationError("Категория не принадлежит пользователю")
        if self.account.user_id != self.user_id:
            raise ValidationError("Счет не принадлежит пользователю")
        if self.category.type_transaction != self.type_transaction:
            raise ValidationError("Тип транзакции не совпадает с типом категории")
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError("Дата начала позже даты окончания")

    def calculate_next_run(self, from_date: date) -> date:
        """Вычисляет следующую дату запуска."""
        if self.schedule_type == self.SCHEDULE_DAILY:
            return from_date + timedelta(days=1)
        if self.schedule_type == self.SCHEDULE_WEEKLY:
            return from_date + timedelta(weeks=1)
        if self.schedule_type == self.SCHEDULE_MONTHLY:
            return from_date + relativedelta(months=1)
        return from_date
