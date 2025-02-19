from django.db import models

from app_user.models import CustomUser


class Account(models.Model):
    """
    Модель для представления счетов пользователя.
    """

    name = models.CharField(max_length=50, verbose_name="Название счета")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, db_index=True, related_name="accounts"
    )
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Баланс"
    )
    is_active = models.BooleanField(default=True, verbose_name="Показать/Скрыть")

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (("name", "user"),)
        verbose_name = "счет"
        verbose_name_plural = "счета"
        ordering = ["name"]
        db_table = "accounts"


class Transfer(models.Model):
    """
    Модель для представления переводов пользователя.
    """

    source_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="transfers_out"
    )
    destination_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="transfers_in"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField()

    class Meta:
        verbose_name = "перевод"
        verbose_name_plural = "переводы"
        ordering = ["timestamp"]

    def __str__(self):
        return f"Transfer of {self.amount} from {self.source_account} to {self.destination_account}"


class Debt(models.Model):
    """
    Модель для представления долгов между счетами.
    """

    transfer = models.OneToOneField(
        Transfer, on_delete=models.CASCADE, related_name="debt"
    )
    borrower_description = models.CharField(max_length=100)

    class Meta:
        verbose_name = "долг"
        verbose_name_plural = "долги"

    def __str__(self):
        return f"Debt of {self.transfer.amount} to {self.borrower_description}"
