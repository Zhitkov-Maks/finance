from accounts.models import Account
from django.db.models.signals import post_save
from django.dispatch import receiver

from transactions.models import Transaction


@receiver(post_save, sender=Transaction)
def start_grace_period_on_expense(sender, instance, created, **kwargs):
    """
    Первый расход с кредитки запускает льготный период.

    Дату берём из транзакции (а не today) — если пользователь ввёл
    задним числом, таймер должен стартовать с реальной даты покупки.
    """
    if not created:
        return

    if not instance.category_id or instance.category.type_transaction != "expense":
        return

    account = instance.account
    if account.account_type != Account.TYPE_CREDIT or account.grace_period_start:
        return

    from django.utils import timezone

    account.grace_period_start = min(instance.create_at.date(), timezone.localdate())
    account.save(update_fields=["grace_period_start"])
