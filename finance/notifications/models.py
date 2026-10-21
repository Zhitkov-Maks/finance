import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_PAYMENT_UPCOMING = "payment_upcoming"
    TYPE_PAYMENT_TODAY = "payment_today"
    TYPE_BUDGET_WARNING = "budget_warning"
    TYPE_BUDGET_EXCEEDED = "budget_exceeded"

    TYPE_CHOICES = [
        (TYPE_PAYMENT_UPCOMING, "Скоро платёж"),
        (TYPE_PAYMENT_TODAY, "Платёж сегодня"),
        (TYPE_BUDGET_WARNING, "Бюджет почти исчерпан"),
        (TYPE_BUDGET_EXCEEDED, "Бюджет превышен"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    is_push_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "notification_type", "created_at"]),
        ]


class NotificationPreferences(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_prefs",
    )
    push_enabled = models.BooleanField(default=True)  # push вкл по умолчанию
    budget_alerts = models.BooleanField(default=True)
    payment_alerts = models.BooleanField(default=True)
    payment_days_before = models.PositiveSmallIntegerField(default=1)  # 1 = завтра
    budget_warning_threshold = models.PositiveSmallIntegerField(default=80)


class PushSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
    )
    endpoint = models.TextField(unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
