import uuid

from django.conf import settings
from django.db import models


class Insight(models.Model):
    TYPE_CATEGORY_SPIKE = "category_spike"
    TYPE_SUBSCRIPTION_INCREASE = "subscription_increase"
    TYPE_TRANSACTION_DUPLICATE = "transaction_duplicate"

    TYPE_CHOICES = [
        (TYPE_CATEGORY_SPIKE, "Скачок в категории"),
        (TYPE_SUBSCRIPTION_INCREASE, "Подписка подорожала"),
        (TYPE_TRANSACTION_DUPLICATE, "Дубликат транзакции"),
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
