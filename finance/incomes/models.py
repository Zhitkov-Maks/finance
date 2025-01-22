from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from app_user.models import CustomUser

from accounts.models import Account


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="categories", db_index=True
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (("name", "user"),)
        verbose_name = "Категория дохода"
        verbose_name_plural = "категории дохода"
        ordering = ("name",)


class Income(models.Model):
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма",
        validators=[MinValueValidator(Decimal(0.01))],
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="incomes",
        db_index=True,
        verbose_name="Пользователь",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="incomes",
        db_index=True,
        verbose_name="Тип дохода",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="incomes",
        db_index=True,
        verbose_name="Счет",
    )
    create_at = models.DateTimeField(auto_now=True, verbose_name="Дата операции")

    def __str__(self):
        return f"{self.amount} {self.category.name} {self.user.email}"

    class Meta:
        verbose_name = "доход"
        verbose_name_plural = "доходы"
        ordering = ["-create_at"]
        db_table = "incomes"
