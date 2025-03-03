from django.db import models

from accounts.models import Account


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
        return (f"Transfer of {self.amount} from "
                f"{self.source_account} to {self.destination_account}")
