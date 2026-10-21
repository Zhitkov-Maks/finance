from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from transactions.models import Transaction


@receiver(post_save, sender=Transaction)
def on_transaction_created(sender, instance, created, **kwargs):
    if not created:
        return
    if not instance.category_id:
        return
    if instance.category.type_transaction != "expense":
        return

    transaction.on_commit(
        lambda: __import__(
            "notifications.tasks", fromlist=["check_budgets_for_user"]
        ).check_budgets_for_user.delay(instance.user_id)
    )
