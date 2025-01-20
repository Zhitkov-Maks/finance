from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from app_user.models import CustomUser
from accounts.models import Account


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название расхода")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="classes", db_index=True
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (("name", "user"),)
        verbose_name = "категория расхода"
        verbose_name_plural = "категории расхода"
        ordering = ("name",)


class Expense(models.Model):
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма расхода",
        validators=[MinValueValidator(Decimal(0.01))],
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="expenses",
        db_index=True,
        verbose_name="Пользователь",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="expenses",
        db_index=True,
        verbose_name="Тип расхода",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="expenses",
        db_index=True,
        verbose_name="Счет",
    )
    create_at = models.DateTimeField(verbose_name="Дата операции")

    def __str__(self):
        return f"{self.amount} {self.category.name} {self.user.email}"

    class Meta:
        verbose_name = "расход"
        verbose_name_plural = "расходы"
        ordering = ["-create_at"]
        db_table = "expenses"
