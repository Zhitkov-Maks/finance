from app_user.models import CustomUser
from django.db import models


class Account(models.Model):
    """
    Модель для представления счетов пользователя.
    """

    TYPE_STANDARD = "standard"
    TYPE_DEPOSIT = "deposit"  # Вклад (ежедневный процент)
    TYPE_CREDIT = "credit_card"  # Кредитная карта (льготный период)

    ACCOUNT_TYPES = [
        (TYPE_STANDARD, "Обычный"),
        (TYPE_DEPOSIT, "Вклад (проценты)"),
        (TYPE_CREDIT, "Кредитная карта"),
    ]

    name = models.CharField(max_length=50, verbose_name="Название счета")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, db_index=True, related_name="accounts"
    )
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Баланс"
    )
    is_active = models.BooleanField(default=True, verbose_name="Показать/Скрыть")
    is_system_account = models.BooleanField(default=False)

    # --- НОВЫЕ ПОЛЯ ---
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPES,
        default=TYPE_STANDARD,
        verbose_name="Тип счета",
    )

    # Для вкладов
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Годовая ставка, %",
    )

    # Для кредитных карт
    credit_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Кредитный лимит",
    )
    grace_period_days = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Льготный период, дней"
    )
    # Дата, с которой начался текущий беспроцентный период
    grace_period_start = models.DateField(
        null=True, blank=True, verbose_name="Начало льготного периода"
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (("name", "user"),)
        verbose_name = "счет"
        verbose_name_plural = "счета"
        ordering = ["name"]
        db_table = "accounts"
