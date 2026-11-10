from app_user.models import CustomUser
from django.db import models
from django.db.models import Q


class Account(models.Model):
    TYPE_STANDARD = "standard"
    TYPE_DEPOSIT = "deposit"
    TYPE_CREDIT = "credit_card"
    TYPE_DEPOSIT_MONTHLY = "deposit_monthly"

    ACCOUNT_TYPES = [
        (TYPE_STANDARD, "Обычный"),
        (TYPE_DEPOSIT, "Вклад (проценты)"),
        (TYPE_DEPOSIT_MONTHLY, "Вклад (ежемесячный %)"),
        (TYPE_CREDIT, "Кредитная карта"),
    ]

    name = models.CharField(max_length=50, verbose_name="Название счета")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, db_index=True, related_name="accounts"
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True, verbose_name="Показать/Скрыть")
    is_system_account = models.BooleanField(default=False)

    account_type = models.CharField(
        max_length=20, choices=ACCOUNT_TYPES, default=TYPE_STANDARD
    )

    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    credit_limit = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    grace_period_days = models.PositiveIntegerField(null=True, blank=True)
    grace_period_start = models.DateField(null=True, blank=True)
    credit_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    min_payment_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.00, null=True, blank=True
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Дата архивации",
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "user"],
                condition=Q(deleted_at__isnull=True),
                name="unique_active_account_name_per_user",
            ),
        ]
        verbose_name = "счет"
        verbose_name_plural = "счета"
        ordering = ["name"]
        db_table = "accounts"
