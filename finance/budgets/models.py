from app_user.models import CustomUser
from django.db import models
from transactions.models import Category


class Budget(models.Model):
    PERIOD_MONTHLY = "monthly"
    PERIOD_WEEKLY = "weekly"
    PERIOD_CHOICES = [
        (PERIOD_MONTHLY, "Месячный"),
        (PERIOD_WEEKLY, "Недельный"),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    # ✅ Теперь категория необязательна
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="budgets",
        null=True,
        blank=True,
        help_text="Если пусто — это общий бюджет на все расходы",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    period_type = models.CharField(
        max_length=10, choices=PERIOD_CHOICES, default=PERIOD_MONTHLY
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Бюджет"
        verbose_name_plural = "Бюджеты"
        constraints = [
            # Общий бюджет — один на период
            models.UniqueConstraint(
                fields=["user", "period_type"],
                condition=models.Q(category__isnull=True),
                name="uniq_total_budget",
            ),
            # Категорийный — один на (категорию, период)
            models.UniqueConstraint(
                fields=["user", "category", "period_type"],
                condition=models.Q(category__isnull=False),
                name="uniq_category_budget",
            ),
        ]

    @property
    def is_total(self) -> bool:
        return self.category_id is None

    def __str__(self):
        title = self.category.name if self.category else "Общий бюджет"
        return f"{title}: {self.amount} ₽ / {self.get_period_type_display()}"
