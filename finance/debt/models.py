from django.db import models

from transfer.models import Transfer


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
        ordering = ["-transfer__timestamp"]

    def __str__(self):
        return f"Debt of {self.transfer.amount} to {self.borrower_description}"
