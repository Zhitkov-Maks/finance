"""
Views для переводов между счетами и аналитики.

Транзакционная стратегия:
    - Любая мутация баланса идёт через TransferViewMixin + @transaction.atomic.
    - Счета блокируются через select_for_update в детерминированном порядке
      (по PK) — это защищает от дедлоков при встречных переводах.
    - Инвалидация кэшей откладывается через transaction.on_commit.
"""

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from typing import Iterable

from accounts.cache import invalidate_balance_history_cache
from accounts.models import Account
from app_user.models import CustomUser
from django.db import transaction
from django.db.models import Avg, Count, Max, Min, Q, QuerySet, Sum
from django.db.models.functions import TruncDate
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, serializers
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .cache import (
    get_analytics_cache,
    invalidate_transfer_analytics_cache,
    set_analytics_cache,
)
from .models import Transfer
from .schemas import (
    TransferHistoryViewSchema,
    TransferRetrieveViewSchema,
    TransferSchema,
)
from .serializers import TransferSerializer


def _parse_date(value: str | None) -> date | None:
    """YYYY-MM-DD → date. None, если пусто/невалидно."""
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _median(values: list[Decimal]) -> Decimal:
    """Медиана списка Decimal. Пустой список → 0."""
    if not values:
        return Decimal(0)
    sorted_vals = sorted(values)
    mid = len(sorted_vals) // 2
    if len(sorted_vals) % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
    return sorted_vals[mid]


class TransferViewMixin:
    """
    Общие хелперы для любых операций, меняющих балансы счетов.
    """

    @staticmethod
    def _lock_accounts(*account_ids: int) -> dict[int, Account]:
        """
        Заблокировать счета и вернуть их keyed by PK.
        Сортировка PK защищает от дедлоков.
        """
        ids = sorted(set(account_ids))
        return {
            acc.pk: acc
            for acc in Account.objects.select_for_update().filter(pk__in=ids)
        }

    @staticmethod
    def _reconcile_grace_period(
        account: Account, old_balance: Decimal, force_date: date = None
    ) -> None:
        """
        Вызывается после _apply_deltas с балансом ДО применения.
        force_date используется, чтобы таймер стартовал с даты перевода.
        """
        if account.account_type != Account.TYPE_CREDIT:
            return

        from accounts.services import maybe_start_grace_period

        if account.balance < 0:
            maybe_start_grace_period(
                account, old_balance=old_balance, force_date=force_date
            )

    @staticmethod
    def _apply_deltas(
        accounts: dict[int, Account],
        deltas: dict[int, Decimal],
    ) -> None:
        """Применить дельты к заблокированным счетам и сохранить только изменённые."""
        for acc_id, delta in deltas.items():
            if not delta:
                continue
            account = accounts[acc_id]
            account.balance += delta
            account.save(update_fields=["balance"])

    @staticmethod
    def _schedule_cache_invalidation(accounts: Iterable[Account]) -> None:
        """Инвалидировать кэши всех пользователей, чьи счета затронуты."""
        user_ids = {acc.user_id for acc in accounts if acc.user_id is not None}
        if not user_ids:
            return

        def _invalidate() -> None:
            for uid in user_ids:
                invalidate_balance_history_cache(uid)
                invalidate_transfer_analytics_cache(uid)

        transaction.on_commit(_invalidate)


@extend_schema(tags=["Transfer"])
@TransferSchema
class TransferFundsView(TransferViewMixin, generics.CreateAPIView):
    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    @transaction.atomic
    def perform_create(self, serializer: TransferSerializer) -> Transfer:
        source: Account = serializer.validated_data["source_account"]
        destination: Account = serializer.validated_data["destination_account"]
        amount: Decimal = serializer.validated_data["amount"]

        locked = self._lock_accounts(source.pk, destination.pk)

        # 1. Запоминаем балансы ДО изменений
        old_balances = {acc_id: acc.balance for acc_id, acc in locked.items()}

        deltas: dict[int, Decimal] = {
            source.pk: -amount,
            destination.pk: +amount,
        }
        if locked[source.pk].balance + deltas[source.pk] < 0:
            raise serializers.ValidationError(
                {"amount": "Недостаточно средств на счёте списания."}
            )

        transfer = serializer.save()
        self._apply_deltas(locked, deltas)

        # 2. Пересчитываем grace period с учетом старых балансов
        for acc_id, account in locked.items():
            self._reconcile_grace_period(
                account,
                old_balance=old_balances[acc_id],
                force_date=transfer.timestamp.date(),
            )

        self._schedule_cache_invalidation(locked.values())
        return transfer


class TransferPagination(PageNumberPagination):
    page_size: int = 10
    page_size_query_param: str = "page_size"
    max_page_size: int = 100


@extend_schema(tags=["Transfer"])
@TransferHistoryViewSchema
class TransferHistoryView(generics.ListAPIView):
    pagination_class = TransferPagination
    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self) -> QuerySet:
        user: CustomUser = self.request.user
        return Transfer.objects.filter(
            Q(source_account__user=user) | Q(destination_account__user=user),
            source_account__is_system_account=False,
            destination_account__is_system_account=False,
        ).order_by("-timestamp")


@extend_schema(tags=["Transfer"])
@TransferRetrieveViewSchema
class TransferDetailView(TransferViewMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["get", "put", "patch", "delete"]

    def get_queryset(self) -> QuerySet:
        user: CustomUser = self.request.user
        return Transfer.objects.filter(source_account__user=user).order_by("-timestamp")

    @transaction.atomic
    def perform_update(self, serializer: TransferSerializer) -> None:
        transfer: Transfer = self.get_object()

        old_amount: Decimal = transfer.amount
        old_source_id: int = transfer.source_account_id
        old_destination_id: int = transfer.destination_account_id

        new_amount: Decimal = serializer.validated_data.get("amount", old_amount)
        new_source: Account = serializer.validated_data.get(
            "source_account", transfer.source_account
        )
        new_destination: Account = serializer.validated_data.get(
            "destination_account", transfer.destination_account
        )

        if new_source.pk == new_destination.pk:
            raise serializers.ValidationError(
                {
                    "destination_account": "Счета списания и зачисления должны быть разными."
                }
            )

        locked = self._lock_accounts(
            old_source_id,
            old_destination_id,
            new_source.pk,
            new_destination.pk,
        )

        # 1. Запоминаем балансы ДО изменений для всех затронутых счетов
        old_balances = {acc_id: acc.balance for acc_id, acc in locked.items()}

        deltas: dict[int, Decimal] = defaultdict(Decimal)
        deltas[old_source_id] += old_amount
        deltas[old_destination_id] -= old_amount
        deltas[new_source.pk] -= new_amount
        deltas[new_destination.pk] += new_amount

        if locked[new_source.pk].balance + deltas[new_source.pk] < 0:
            raise serializers.ValidationError(
                {"amount": "Недостаточно средств на счёте списания."}
            )

        if locked[new_destination.pk].balance + deltas[new_destination.pk] < 0:
            raise serializers.ValidationError(
                {"amount": "На счёте зачисления недостаточно средств для отката."}
            )

        transfer = serializer.save()
        self._apply_deltas(locked, deltas)

        # 2. Пересчитываем grace period
        for acc_id, account in locked.items():
            self._reconcile_grace_period(
                account,
                old_balance=old_balances[acc_id],
                force_date=transfer.timestamp.date(),
            )

        self._schedule_cache_invalidation(locked.values())

    @transaction.atomic
    def perform_destroy(self, instance: Transfer) -> None:
        source_id: int = instance.source_account_id
        destination_id: int = instance.destination_account_id
        amount: Decimal = instance.amount

        locked = self._lock_accounts(source_id, destination_id)

        # 1. Запоминаем балансы ДО изменений
        old_balances = {acc_id: acc.balance for acc_id, acc in locked.items()}

        instance.delete()
        self._apply_deltas(
            locked,
            {source_id: +amount, destination_id: -amount},
        )

        # 2. Пересчитываем grace period
        for acc_id, account in locked.items():
            self._reconcile_grace_period(
                account,
                old_balance=old_balances[acc_id],
                force_date=instance.timestamp.date(),
            )

        self._schedule_cache_invalidation(locked.values())


# =============================================================================
# АНАЛИТИКА (без изменений)
# =============================================================================


@extend_schema(
    tags=["Transfer"],
    parameters=[
        OpenApiParameter(
            name="date_from",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Начало периода (YYYY-MM-DD), включительно",
        ),
        OpenApiParameter(
            name="date_to",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Конец периода (YYYY-MM-DD), включительно",
        ),
    ],
)
class TransferAnalyticsView(generics.GenericAPIView):
    """
    Аналитика переводов пользователя за период.
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get(self, request, *args, **kwargs):
        user: CustomUser = request.user

        date_to: date = _parse_date(request.query_params.get("date_to")) or date.today()
        date_from: date = _parse_date(request.query_params.get("date_from")) or (
            date_to - timedelta(days=89)
        )
        if date_from > date_to:
            date_from, date_to = date_to, date_from

        cached = get_analytics_cache(user.id, date_from, date_to)
        if cached is not None:
            return Response(cached)

        qs = Transfer.objects.filter(
            Q(source_account__user=user) | Q(destination_account__user=user),
            source_account__is_system_account=False,
            destination_account__is_system_account=False,
            timestamp__date__gte=date_from,
            timestamp__date__lte=date_to,
        ).select_related("source_account", "destination_account")

        aggregates = qs.aggregate(
            count=Count("id"),
            total_amount=Sum("amount"),
            average=Avg("amount"),
            max_amount=Max("amount"),
            min_amount=Min("amount"),
        )

        count: int = aggregates["count"] or 0
        total_amount = aggregates["total_amount"] or Decimal(0)
        average = aggregates["average"] or Decimal(0)
        max_amount = aggregates["max_amount"] or Decimal(0)
        min_amount = aggregates["min_amount"] or Decimal(0)

        amounts = list(qs.values_list("amount", flat=True))
        median = _median(amounts)

        top_accounts = self._build_top_accounts(qs)
        top_pairs = self._build_top_pairs(qs)
        sankey = self._build_sankey(top_accounts, top_pairs)
        daily_activity = self._build_daily_activity(qs, date_from, date_to)

        payload = {
            "period": {
                "date_from": date_from.isoformat(),
                "date_to": date_to.isoformat(),
                "days": (date_to - date_from).days + 1,
            },
            "metrics": {
                "count": count,
                "total_amount": float(total_amount),
                "average": float(average),
                "median": float(median),
                "max": float(max_amount),
                "min": float(min_amount),
            },
            "top_accounts": top_accounts,
            "top_pairs": top_pairs,
            "sankey": sankey,
            "daily_activity": daily_activity,
        }

        set_analytics_cache(user.id, date_from, date_to, payload)
        return Response(payload)

    @staticmethod
    def _build_top_accounts(qs: QuerySet) -> list[dict]:
        outgoing_rows = qs.values("source_account_id", "source_account__name").annotate(
            total=Sum("amount"), cnt=Count("id")
        )

        incoming_rows = qs.values(
            "destination_account_id", "destination_account__name"
        ).annotate(total=Sum("amount"), cnt=Count("id"))

        by_id: dict[int, dict] = {}

        def ensure(acc_id: int, name: str) -> dict:
            if acc_id not in by_id:
                by_id[acc_id] = {
                    "id": acc_id,
                    "name": name,
                    "incoming": Decimal(0),
                    "outgoing": Decimal(0),
                    "count": 0,
                }
            return by_id[acc_id]

        for row in outgoing_rows:
            entry = ensure(row["source_account_id"], row["source_account__name"])
            entry["outgoing"] += row["total"] or Decimal(0)
            entry["count"] += row["cnt"] or 0

        for row in incoming_rows:
            entry = ensure(
                row["destination_account_id"],
                row["destination_account__name"],
            )
            entry["incoming"] += row["total"] or Decimal(0)
            entry["count"] += row["cnt"] or 0

        total_turnover = sum(
            (e["incoming"] + e["outgoing"]) for e in by_id.values()
        ) or Decimal(1)

        result = []
        for entry in by_id.values():
            turnover = entry["incoming"] + entry["outgoing"]
            result.append(
                {
                    "id": entry["id"],
                    "name": entry["name"],
                    "incoming": float(entry["incoming"]),
                    "outgoing": float(entry["outgoing"]),
                    "turnover": float(turnover),
                    "count": entry["count"],
                    "turnover_percent": round(
                        float(turnover / total_turnover * 100), 1
                    ),
                }
            )

        result.sort(key=lambda x: x["turnover"], reverse=True)
        return result

    @staticmethod
    def _build_top_pairs(qs: QuerySet, limit: int = 10) -> list[dict]:
        rows = (
            qs.values(
                "source_account_id",
                "source_account__name",
                "destination_account_id",
                "destination_account__name",
            )
            .annotate(total=Sum("amount"), cnt=Count("id"))
            .order_by("-total")
        )

        total_amount = sum((r["total"] or Decimal(0)) for r in rows) or Decimal(1)

        result = []
        for row in rows[:limit]:
            amount = row["total"] or Decimal(0)
            result.append(
                {
                    "key": f"{row['source_account_id']}→{row['destination_account_id']}",
                    "source_id": row["source_account_id"],
                    "source": row["source_account__name"],
                    "destination_id": row["destination_account_id"],
                    "destination": row["destination_account__name"],
                    "amount": float(amount),
                    "count": row["cnt"] or 0,
                    "percent": round(float(amount / total_amount * 100), 1),
                }
            )

        return result

    @staticmethod
    def _build_sankey(
        top_accounts: list[dict],
        top_pairs: list[dict],
        node_limit: int = 8,
    ) -> dict:
        top_nodes = top_accounts[:node_limit]
        node_ids = {n["id"] for n in top_nodes}

        links = [
            {
                "source": pair["source_id"],
                "destination": pair["destination_id"],
                "amount": pair["amount"],
            }
            for pair in top_pairs
            if pair["source_id"] in node_ids and pair["destination_id"] in node_ids
        ]

        nodes = [
            {
                "id": n["id"],
                "name": n["name"],
                "incoming": n["incoming"],
                "outgoing": n["outgoing"],
                "total": n["turnover"],
            }
            for n in top_nodes
        ]

        return {"nodes": nodes, "links": links}

    @staticmethod
    def _build_daily_activity(
        qs: QuerySet,
        date_from: date,
        date_to: date,
    ) -> list[dict]:
        rows = (
            qs.annotate(day=TruncDate("timestamp"))
            .values("day")
            .annotate(count=Count("id"), amount=Sum("amount"))
            .order_by("day")
        )

        by_day = {r["day"]: r for r in rows}

        result = []
        current = date_from
        while current <= date_to:
            row = by_day.get(current)
            result.append(
                {
                    "date": current.isoformat(),
                    "count": (row["count"] if row else 0),
                    "amount": float(row["amount"]) if row and row["amount"] else 0.0,
                }
            )
            current += timedelta(days=1)

        return result
