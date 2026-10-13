import decimal
from datetime import date, timedelta

from accounts.cache import invalidate_balance_history_cache
from accounts.models import Account
from app_user.models import CustomUser
from django.db.models import Avg, Count, Max, Min, Q, QuerySet, Sum
from django.db.models.functions import TruncDate
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
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


# =============================================================================
# Хелперы
# =============================================================================
def _parse_date(value: str | None) -> date | None:
    """YYYY-MM-DD → date. None, если пусто/невалидно."""
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _median(values: list[decimal.Decimal]) -> decimal.Decimal:
    """Медиана списка Decimal. Пустой список → 0."""
    if not values:
        return decimal.Decimal(0)
    sorted_vals = sorted(values)
    mid = len(sorted_vals) // 2
    if len(sorted_vals) % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
    return sorted_vals[mid]


# =============================================================================
# TransferFundsView
# =============================================================================
@extend_schema(tags=["Transfer"])
@TransferSchema
class TransferFundsView(generics.CreateAPIView):
    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def perform_create(self, serializer):
        source_account: Account = serializer.validated_data["source_account"]
        destination_account: Account = serializer.validated_data["destination_account"]
        amount = serializer.validated_data["amount"]

        source_account.balance -= amount
        destination_account.balance += amount

        source_account.save()
        destination_account.save()

        transfer = serializer.save()
        invalidate_balance_history_cache(source_account.user_id)
        invalidate_transfer_analytics_cache(source_account.user_id)  # ← добавили

        return transfer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# =============================================================================
# Пагинация
# =============================================================================
class TransferPagination(PageNumberPagination):
    page_size: int = 10
    page_size_query_param: str = "page_size"
    max_page_size: int = 100


# =============================================================================
# TransferHistoryView
# =============================================================================
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


# =============================================================================
# TransferDetailView
# =============================================================================
@extend_schema(tags=["Transfer"])
@TransferRetrieveViewSchema
class TransferDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names: list = ["get", "put", "delete"]

    def get_queryset(self) -> QuerySet:
        user: CustomUser = self.request.user
        return (
            Transfer.objects.filter(source_account__user=user)
            .order_by("-timestamp")
        )

    def perform_update(self, serializer):
        transfer: Transfer = self.get_object()

        old_amount: decimal = transfer.amount
        new_amount: decimal = serializer.validated_data["amount"]

        source_account: Account = transfer.source_account
        destination_account: Account = transfer.destination_account

        if new_amount != old_amount:
            source_account.balance += old_amount - new_amount
            destination_account.balance -= old_amount - new_amount

            source_account.save()
            destination_account.save()

        serializer.save()

        invalidate_balance_history_cache(source_account.user_id)
        invalidate_transfer_analytics_cache(source_account.user_id)

    def perform_destroy(self, instance):
        source_account: Account = instance.source_account
        destination_account: Account = instance.destination_account

        source_account.balance += instance.amount
        destination_account.balance -= instance.amount

        source_account.save()
        destination_account.save()

        user_id = source_account.user_id
        instance.delete()

        invalidate_balance_history_cache(user_id)
        invalidate_transfer_analytics_cache(user_id)


# =============================================================================
# TransferAnalyticsView
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

    По умолчанию — последние 90 дней. Всё считается в SQL, кроме медианы
    (отдельный лёгкий запрос values_list).

    Возвращает:
        - period: границы периода
        - metrics: count, total_amount, average, median, max, min
        - top_accounts: топ счетов по обороту (входящие + исходящие)
        - top_pairs: топ пар source → destination
        - sankey: nodes + links для диаграммы
        - daily_activity: активность по дням (включая пустые дни)
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get(self, request, *args, **kwargs):
        user: CustomUser = request.user

        # --- Период ---
        date_to: date = _parse_date(request.query_params.get("date_to")) or date.today()
        date_from: date = _parse_date(request.query_params.get("date_from")) or (
            date_to - timedelta(days=89)
        )
        if date_from > date_to:
            date_from, date_to = date_to, date_from

        # --- Пробуем достать из кэша ---
        cached = get_analytics_cache(user.id, date_from, date_to)
        if cached is not None:
            return Response(cached)

        # --- Считаем ---
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
        total_amount = aggregates["total_amount"] or decimal.Decimal(0)
        average = aggregates["average"] or decimal.Decimal(0)
        max_amount = aggregates["max_amount"] or decimal.Decimal(0)
        min_amount = aggregates["min_amount"] or decimal.Decimal(0)

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

        # --- Кладём в кэш ---
        set_analytics_cache(user.id, date_from, date_to, payload)

        return Response(payload)

    # =========================================================================
    # Топ счетов по обороту
    # =========================================================================
    @staticmethod
    def _build_top_accounts(qs: QuerySet) -> list[dict]:
        """
        Список счетов с входящими/исходящими/оборотом.
        Один счёт может быть и источником, и получателем — суммируем.
        """
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
                    "incoming": decimal.Decimal(0),
                    "outgoing": decimal.Decimal(0),
                    "count": 0,
                }
            return by_id[acc_id]

        for row in outgoing_rows:
            entry = ensure(row["source_account_id"], row["source_account__name"])
            entry["outgoing"] += row["total"] or decimal.Decimal(0)
            entry["count"] += row["cnt"] or 0

        for row in incoming_rows:
            entry = ensure(
                row["destination_account_id"],
                row["destination_account__name"],
            )
            entry["incoming"] += row["total"] or decimal.Decimal(0)
            entry["count"] += row["cnt"] or 0

        total_turnover = sum(
            (e["incoming"] + e["outgoing"]) for e in by_id.values()
        ) or decimal.Decimal(1)

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

    # =========================================================================
    # Топ пар source → destination
    # =========================================================================
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

        total_amount = sum(
            (r["total"] or decimal.Decimal(0)) for r in rows
        ) or decimal.Decimal(1)

        result = []
        for row in rows[:limit]:
            amount = row["total"] or decimal.Decimal(0)
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

    # =========================================================================
    # Sankey: nodes + links
    # =========================================================================
    @staticmethod
    def _build_sankey(
        top_accounts: list[dict],
        top_pairs: list[dict],
        node_limit: int = 8,
    ) -> dict:
        """
        Строит nodes/links для Sankey из уже посчитанных top_accounts и top_pairs.
        Ограничиваем топ-N узлов, связи — только между ними.
        """
        top_nodes = top_accounts[:node_limit]
        node_ids = {n["id"] for n in top_nodes}

        links = []
        for pair in top_pairs:
            if pair["source_id"] in node_ids and pair["destination_id"] in node_ids:
                links.append(
                    {
                        "source": pair["source_id"],
                        "destination": pair["destination_id"],
                        "amount": pair["amount"],
                    }
                )

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

    # =========================================================================
    # Дневная активность
    # =========================================================================
    @staticmethod
    def _build_daily_activity(
        qs: QuerySet,
        date_from: date,
        date_to: date,
    ) -> list[dict]:
        """
        Массив по каждому дню периода, включая дни без переводов.
        """
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
