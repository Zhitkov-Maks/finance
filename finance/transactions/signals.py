from accounts.models import Account
from django.db.models.signals import post_save
from django.dispatch import receiver

from transactions.models import Transaction


@receiver(post_save, sender=Transaction)
def start_grace_period_on_expense(sender, instance, created, **kwargs):
    """
    Сигнал срабатывает после сохранения любой транзакции.
    Если это первый расход по кредитной карте, запускает льготный период.
    """
    # 1. Реагируем только на создание (created=True), а не на обновление
    if not created:
        return

    # 2. Проверяем, что у транзакции есть категория и это именно расход (expense)
    if not instance.category_id or instance.category.type_transaction != "expense":
        return

    # 3. Получаем счет, к которому привязана транзакция
    account = instance.account

    # 4. Если это кредитная карта и льготный период еще не запущен (None)
    if account.account_type == Account.TYPE_CREDIT and not account.grace_period_start:
        # Запускаем таймер с даты совершения транзакции
        # instance.create_at - это datetime, поэтому берем .date()
        account.grace_period_start = instance.create_at.date()

        # Сохраняем только измененное поле, чтобы не перезаписать баланс (если он меняется параллельно)
        account.save(update_fields=["grace_period_start"])
