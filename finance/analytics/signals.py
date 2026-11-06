from accounts.models import Account
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from recurring.models import RecurringTransaction
from transactions.models import Transaction


def invalidate_forecast_cache(user_id):
    """Сносит кэш прогноза для конкретного пользователя."""
    cache.delete_pattern(f"forecast:{user_id}:*")


@receiver(post_save, sender=Transaction)
@receiver(post_delete, sender=Transaction)
def clear_forecast_on_transaction(sender, instance, **kwargs):
    invalidate_forecast_cache(instance.user_id)


@receiver(post_save, sender=RecurringTransaction)
@receiver(post_delete, sender=RecurringTransaction)
def clear_forecast_on_recurring(sender, instance, **kwargs):
    invalidate_forecast_cache(instance.user_id)


@receiver(post_save, sender=Account)
@receiver(post_delete, sender=Account)
def clear_forecast_on_account(sender, instance, **kwargs):
    if not instance.is_system_account:
        invalidate_forecast_cache(instance.user_id)
