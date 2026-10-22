import logging

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from recurring.models import RecurringTransaction
from transactions.models import Transaction

logger = logging.getLogger(__name__)

DUPLICATE_MIN_AMOUNT = 10


# === Детектор 2: Подписка подорожала ===


@receiver(pre_save, sender=RecurringTransaction)
def track_amount_before_save(sender, instance, **kwargs):
    """
    Запоминаем старое значение amount, чтобы потом сравнить.
    Хранится в instance._old_amount_for_insight — ephemeral, только в памяти.
    """
    if not instance.pk:
        instance._old_amount_for_insight = None
        return
    try:
        old = RecurringTransaction.objects.only("amount").get(pk=instance.pk)
        instance._old_amount_for_insight = old.amount
    except RecurringTransaction.DoesNotExist:
        instance._old_amount_for_insight = None


@receiver(post_save, sender=RecurringTransaction)
def detect_subscription_increase(sender, instance, created, **kwargs):
    if created:
        return

    old_amount = getattr(instance, "_old_amount_for_insight", None)
    if old_amount is None or old_amount <= 0:
        return

    new_amount = instance.amount
    if not new_amount or new_amount <= 0 or new_amount == old_amount:
        return

    # Быстрая проверка — если меньше 5%, не тратим Celery-ресурс
    increase_ratio = float(new_amount) / float(old_amount)
    if increase_ratio <= 1.05:
        return

    # Отправляем в Celery ПОСЛЕ коммита транзакции
    transaction.on_commit(
        lambda: __import__(
            "insights.tasks", fromlist=["async_detect_subscription_increase"]
        ).async_detect_subscription_increase.delay(instance.pk, str(old_amount))
    )


# === Детектор 3: Дубликат транзакции ===


@receiver(post_save, sender=Transaction)
def detect_transaction_duplicate(sender, instance, created, **kwargs):
    """
    Тонкий сигнал: только быстрые проверки + откладывает тяжёлый запрос в Celery.
    Тяжёлый SQL (поиск дубликатов в окне) выполняется в async_detect_transaction_duplicate.
    """
    if not created:
        return

    if not instance.amount or not instance.account_id:
        return
    if instance.amount < DUPLICATE_MIN_AMOUNT:
        return

    # Откладываем на on_commit — задача увидит транзакцию только если она реально закоммичена
    transaction.on_commit(
        lambda: __import__(
            "insights.tasks", fromlist=["async_detect_transaction_duplicate"]
        ).async_detect_transaction_duplicate.delay(str(instance.pk))
    )
