from datetime import datetime, time

from accounts.cache import invalidate_balance_history_cache
from accounts.models import Account
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from transactions.models import Transaction
from transactions.views import _apply_transaction_to_balance

from .models import RecurringTransaction


@shared_task
def process_recurring_transactions():
    """
    Ежедневная задача: находит все активные регулярные операции,
    у которых next_run_date <= сегодня, и создаёт реальные транзакции.
    """
    today = timezone.localdate()  # ← учитывает TIME_ZONE, а не UTC

    qs = (
        RecurringTransaction.objects.filter(is_active=True, next_run_date__lte=today)
        .select_related("account", "category")
        .order_by("next_run_date")
    )

    created_count = 0

    for rec in qs:
        with transaction.atomic():
            # Достигли end_date — деактивируем и пропускаем
            if rec.end_date and rec.next_run_date > rec.end_date:
                rec.is_active = False
                rec.save(update_fields=["is_active"])
                continue

            tz = timezone.get_current_timezone()
            create_at = timezone.make_aware(
                datetime.combine(rec.next_run_date, time(hour=12)), tz
            )

            # 1. Создаём транзакцию с явным type_transaction
            tx = Transaction.objects.create(
                user_id=rec.user_id,
                account=rec.account,
                category=rec.category,
                type_transaction=rec.type_transaction,
                amount=rec.amount,
                create_at=create_at,
                comment=f"[Авто] {rec.title}. {rec.comment}".strip(),
                recurring_source=rec,
            )

            # 2. Применяем к балансу через общую функцию
            #    (обрабатывает кредитные счета и grace period)
            old_balance = Account.objects.get(pk=rec.account_id).balance
            _apply_transaction_to_balance(tx, old_balance=old_balance)

            # 3. Инвалидация кэша — строго после коммита
            user_id = rec.user_id
            transaction.on_commit(
                lambda uid=user_id: invalidate_balance_history_cache(uid)
            )

            # 4. Переносим next_run_date
            rec.last_run_date = rec.next_run_date
            rec.next_run_date = rec.calculate_next_run(rec.next_run_date)
            if rec.end_date and rec.next_run_date > rec.end_date:
                rec.is_active = False
            rec.save(update_fields=["last_run_date", "next_run_date", "is_active"])

            created_count += 1

    return f"Created {created_count} transactions"
