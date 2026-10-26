import uuid

from django.conf import settings
from django.db import models


class Insight(models.Model):
    TYPE_CATEGORY_SPIKE = "category_spike"
    TYPE_SUBSCRIPTION_INCREASE = "subscription_increase"
    TYPE_TRANSACTION_DUPLICATE = "transaction_duplicate"
    TYPE_SALARY_SPIKE = "salary_spike"
    TYPE_HIDDEN_LEAK = "hidden_leak"
    TYPE_BUDGET_OVERSPEND = "budget_overspend"
    TYPE_CASH_GAP = "cash_gap"
    TYPE_DEPOSIT_FORECAST = "deposit_forecast"
    TYPE_CREDIT_CARD_GRACE = "credit_card_grace"
    TYPE_MONTHLY_REPORT = "monthly_report"
    TYPE_SAVINGS_IMPROVED = "savings_improved"
    TYPE_IDLE_CASH = "idle_cash"
    TYPE_DEBT_VS_DEPOSIT = "debt_vs_deposit"
    TYPE_BUDGET_REALLOCATION = "budget_reallocation"

    TYPE_CHOICES = [
        (TYPE_CATEGORY_SPIKE, "Скачок в категории"),
        (TYPE_SUBSCRIPTION_INCREASE, "Подписка подорожала"),
        (TYPE_TRANSACTION_DUPLICATE, "Дубликат транзакции"),
        (TYPE_SALARY_SPIKE, "Траты после зарплаты"),
        (TYPE_HIDDEN_LEAK, "Скрытая утечка"),
        (TYPE_BUDGET_OVERSPEND, "Бюджет будет превышен"),
        (TYPE_CASH_GAP, "Кассовый разрыв"),
        (TYPE_DEPOSIT_FORECAST, "Прогноз вклада"),
        (TYPE_CREDIT_CARD_GRACE, "Льготный период кредитки"),
        (TYPE_MONTHLY_REPORT, "Финансовый отчёт"),
        (TYPE_SAVINGS_IMPROVED, "Экономия улучшилась"),
        (TYPE_IDLE_CASH, "Свободные деньги простаивают"),
        (TYPE_DEBT_VS_DEPOSIT, "Долг дороже вклада"),
        (TYPE_BUDGET_REALLOCATION, "Можно отложить"),
    ]

    SEVERITY_INFO = "info"
    SEVERITY_WARNING = "warning"
    SEVERITY_CRITICAL = "critical"

    SEVERITY_CHOICES = [
        (SEVERITY_INFO, "Информация"),
        (SEVERITY_WARNING, "Предупреждение"),
        (SEVERITY_CRITICAL, "Критично"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="insights",
    )
    insight_type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    severity = models.CharField(
        max_length=16, choices=SEVERITY_CHOICES, default=SEVERITY_INFO
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    action_url = models.CharField(max_length=255, blank=True)
    period_key = models.CharField(max_length=128, blank=True, db_index=True)
    is_dismissed = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_dismissed", "-created_at"]),
            models.Index(fields=["user", "insight_type", "created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "period_key"],
                condition=models.Q(period_key__gt=""),
                name="unique_insight_period_key_per_user",
            ),
        ]

    def __str__(self):
        return f"{self.user_id} | {self.insight_type} | {self.title}"


class FinancialGoal(models.Model):
    GOAL_SAVE = "save"
    GOAL_LIMIT = "limit"

    GOAL_TYPES = [
        (GOAL_SAVE, "Сэкономить сумму"),
        (GOAL_LIMIT, "Не превысить лимит"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals"
    )
    goal_type = models.CharField(max_length=10, choices=GOAL_TYPES, default=GOAL_SAVE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(
        "transactions.Category", on_delete=models.SET_NULL, null=True, blank=True
    )
    month = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "month")


class InsightSettings(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="insight_settings",
    )
    small_expense_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=300,
        verbose_name="Порог мелких трат (₽)",
    )
    idle_cash_threshold = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=50000,
        verbose_name="Порог простаивающих денег (₽)",
    )
