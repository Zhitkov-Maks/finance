# forecast/tasks.py
import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from recurring.models import RecurringTransaction

from .forecast import ForecastService

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def warm_recurring_cache():
    """
    Прогревает кэш recurring-статистики для всех пользователей
    с активными регулярными операциями.

    Запускается в 01:00 — после того как process_recurring_transactions
    сдвинул next_run_date и сигналы сбросили старый кэш.
    """
    user_ids = (
        RecurringTransaction.objects.filter(is_active=True)
        .values_list("user_id", flat=True)
        .distinct()
    )

    warmed = 0
    for user_id in user_ids:
        try:
            user = User.objects.get(pk=user_id)
            ForecastService(user)._get_recurring_stats()
            warmed += 1
        except Exception:
            logger.exception("warm_recurring_cache failed for user=%s", user_id)

    return f"Warmed recurring cache for {warmed}/{len(user_ids)} users"
