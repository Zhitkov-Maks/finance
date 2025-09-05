from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from app_user.models import CustomUser
from accounts.models import Account


class Category(models.Model):
    """
    Модель для представления категорий транзакций пользователя.
    """
    name = models.CharField(max_length=100, verbose_name="Название категории")
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="cats",
        db_index=True
    )
    type_transaction = models.CharField(
        max_length=20,
        verbose_name="Тип операции"
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'user', 'type_transaction'],
                name='unique_category_per_user_and_type'
            )
        ]
        verbose_name = "категория транзакции"
        verbose_name_plural = "категории транзакций"
        ordering = ("name",)


class Transaction(models.Model):
    """
    Модель для представления транзакций пользователя.
    """

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма транзакции",
        validators=[MinValueValidator(Decimal(0.01))],
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="transactions",
        db_index=True,
        verbose_name="Пользователь",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="transactions",
        db_index=True,
        verbose_name="Тип расхода",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
        db_index=True,
        verbose_name="Счет",
    )
    create_at = models.DateTimeField(verbose_name="Дата операции")
    comment = models.TextField(
        max_length=200,
        verbose_name="Комментарий",
        default="",
        blank=True,
        null=True,
    )

    def __str__(self):
        return (f"{self.amount} {self.type_transaction}"
                "{self.category.name} {self.user.email}")

    class Meta:
        verbose_name = "транзакция"
        verbose_name_plural = "транзакции"
        ordering = ["-create_at", "-amount", "category__name"]
        db_table = "transactions"
