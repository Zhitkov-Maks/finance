from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from app_user.models import CustomUser
from accounts.models import Account


class Category(models.Model):
    """
    Модель для представления категорий транзакций пользователя.
    Поддерживает вложенность через self-referential ForeignKey.
    """
    name = models.CharField(max_length=100, verbose_name="Название категории")
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="categories",
        db_index=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Родительская категория"
    )
    type_transaction = models.CharField(
        max_length=20,
        verbose_name="Тип операции"
    )
    level = models.PositiveIntegerField(
        default=0,
        verbose_name="Уровень вложенности"
    )

    def save(self, *args, **kwargs):
        """Автоматически устанавливаем уровень вложенности."""
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"{self.parent} → {self.name}"
        return self.name

    def get_full_path(self):
        """Возвращает полный путь категории"""
        if self.parent:
            return f"{self.parent.get_full_path()} → {self.name}"
        return self.name
    
    def get_all_children(self):
        """Рекурсивно получает все дочерние категории"""
        children = list(self.children.all())
        for child in children:
            children.extend(child.get_all_children())
        return children

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'user', 'type_transaction', 'parent'],
                name='unique_subcategory_per_user_and_type'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'parent']),
            models.Index(fields=['level']),
        ]
        verbose_name = "категория транзакции"
        verbose_name_plural = "категории транзакций"
        ordering = ("level", "name")


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
