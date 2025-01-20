from django.db import models

from app_user.models import CustomUser


class Account(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название счета")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, db_index=True, related_name="accounts"
    )
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Баланс"
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (("name", "user"),)
        verbose_name = "счет"
        verbose_name_plural = "счета"
        ordering = ["name"]
        db_table = "accounts"
