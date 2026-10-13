from decimal import Decimal

from asgiref.sync import sync_to_async
from django.db.models import Q, Sum

ZERO = Decimal(0)

# ---------- Счета ----------


def _fetch_accounts_sync(user, account_id, include_inactive):
    from accounts.models import Account

    qs = Account.objects.filter(user=user, is_system_account=False)
    if account_id:
        qs = qs.filter(pk=account_id)
    if not include_inactive:
        qs = qs.filter(is_active=True)
    return list(qs.order_by("name"))


# ---------- Агрегаты "после date_to" ----------


def _agg_transactions_after_sync(user, account_ids, after_dt):
    """Один запрос: (income_map, expense_map)."""
    from transactions.models import Transaction

    rows = (
        Transaction.objects.filter(
            user=user,
            account_id__in=account_ids,
            category__type_transaction__in=("income", "expense"),
            create_at__gt=after_dt,
        )
        .values("account_id", "category__type_transaction")
        .annotate(total=Sum("amount"))
    )
    income_map, expense_map = {}, {}
    for r in rows:
        bucket = (
            income_map if r["category__type_transaction"] == "income" else expense_map
        )
        bucket[r["account_id"]] = r["total"] or ZERO
    return income_map, expense_map


def _agg_transfers_after_sync(user, account_ids, after_dt):
    """Один запрос: (incoming_map, outgoing_map)."""
    from transfer.models import Transfer

    ids = set(account_ids)
    rows = (
        Transfer.objects.filter(timestamp__gt=after_dt)
        .filter(Q(source_account_id__in=ids) | Q(destination_account_id__in=ids))
        .values("source_account_id", "destination_account_id")
        .annotate(total=Sum("amount"))
    )
    incoming_map, outgoing_map = {}, {}
    for r in rows:
        total = r["total"] or ZERO
        if r["destination_account_id"] in ids:
            incoming_map[r["destination_account_id"]] = total
        if r["source_account_id"] in ids:
            outgoing_map[r["source_account_id"]] = total
    return incoming_map, outgoing_map


# ---------- Операции за период ----------


def _fetch_transactions_in_period_sync(user, account_ids, dt_from, dt_to):
    from transactions.models import Transaction

    return list(
        Transaction.objects.filter(
            user=user,
            account_id__in=account_ids,
            create_at__gte=dt_from,
            create_at__lte=dt_to,
        ).values("account_id", "amount", "create_at", "category__type_transaction")
    )


def _fetch_transfers_in_period_sync(user, account_ids, dt_from, dt_to):
    from transfer.models import Transfer

    return list(
        Transfer.objects.filter(timestamp__gte=dt_from, timestamp__lte=dt_to)
        .filter(
            Q(source_account_id__in=account_ids)
            | Q(destination_account_id__in=account_ids)
        )
        .values("source_account_id", "destination_account_id", "amount", "timestamp")
    )


# ============================================================
# Меняйте на True, только если вызываете внутри transaction.atomic().

_THREAD_SENSITIVE = False

fetch_accounts = sync_to_async(_fetch_accounts_sync, thread_sensitive=_THREAD_SENSITIVE)
agg_transactions_after = sync_to_async(
    _agg_transactions_after_sync, thread_sensitive=_THREAD_SENSITIVE
)
agg_transfers_after = sync_to_async(
    _agg_transfers_after_sync, thread_sensitive=_THREAD_SENSITIVE
)
fetch_transactions_in_period = sync_to_async(
    _fetch_transactions_in_period_sync, thread_sensitive=_THREAD_SENSITIVE
)
fetch_transfers_in_period = sync_to_async(
    _fetch_transfers_in_period_sync, thread_sensitive=_THREAD_SENSITIVE
)
