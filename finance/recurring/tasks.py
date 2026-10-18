from datetime import date, datetime, time

from accounts.models import Account
from celery import shared_task
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from transactions.models import Transaction

from .models import RecurringTransaction


@shared_task
def process_recurring_transactions():
    """
    Ежедневная задача: находит все активные регулярные операции,
    у которых next_run_date <= сегодня, и создает реальные транзакции.
    """
    today = date.today()

    qs = RecurringTransaction.objects.filter(
        is_active=True,
        next_run_date__lte=today,
    ).select_related("account", "category")

    created_count = 0

    for rec in qs:
        with transaction.atomic():
            # Если достигли end_date — выключаем и пропускаем
            if rec.end_date and rec.next_run_date > rec.end_date:
                rec.is_active = False
                rec.save(update_fields=["is_active"])
                continue

            # Время транзакции — 12:00 текущего дня (чтобы не было граничных эффектов)
            tz = timezone.get_current_timezone()
            create_at = timezone.make_aware(
                datetime.combine(rec.next_run_date, time(hour=12)), tz
            )

            # 1. Создаем транзакцию
            Transaction.objects.create(
                user=rec.user,
                account=rec.account,
                category=rec.category,
                amount=rec.amount,
                create_at=create_at,
                comment=f"[Авто] {rec.title}. {rec.comment}".strip(),
            )

            # 2. Обновляем баланс счета
            # (Если у тебя создание Transaction в TransactionViewSet уже делает это,
            #  тогда эту часть можно убрать. Но в cron'е лучше явно).
            if rec.type_transaction == "income":
                Account.objects.filter(pk=rec.account_id).update(
                    balance=F("balance") + rec.amount
                )
            else:
                Account.objects.filter(pk=rec.account_id).update(
                    balance=F("balance") - rec.amount
                )

            # 3. Обновляем next_run_date
            rec.last_run_date = rec.next_run_date
            rec.next_run_date = rec.calculate_next_run(rec.next_run_date)

            # Если следующая дата вышла за end_date — деактивируем
            if rec.end_date and rec.next_run_date > rec.end_date:
                rec.is_active = False

            rec.save(update_fields=["last_run_date", "next_run_date", "is_active"])
            created_count += 1

    return f"Created {created_count} transactions"
