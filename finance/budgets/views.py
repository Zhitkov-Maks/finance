from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from transactions.models import Category, Transaction

from .models import Budget
from .serializers import BudgetSerializer


# ============================================================================
# Вспомогательные
# ============================================================================
def _period_bounds(period_type: str, reference: date) -> tuple[date, date]:
    """Границы периода: (start_date, end_date) включительно."""
    if period_type == Budget.PERIOD_MONTHLY:
        start = reference.replace(day=1)
        if start.month == 12:
            end = date(start.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(start.year, start.month + 1, 1) - timedelta(days=1)
        return start, end

    if period_type == Budget.PERIOD_WEEKLY:
        # Monday — первый день недели (ISO)
        start = reference - timedelta(days=reference.weekday())
        end = start + timedelta(days=6)
        return start, end

    raise ValueError(f"Unknown period_type: {period_type}")


def _to_aware_range(start: date, end: date):
    """Границы [start 00:00, end 23:59:59.999999] в текущей TZ."""
    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(start, time.min), tz)
    end_dt = timezone.make_aware(datetime.combine(end, time.max), tz)
    return start_dt, end_dt


def _collect_descendant_ids(categories: list[Category], root_id: int) -> set[int]:
    """
    Возвращает {root_id} ∪ все ID потомков.

    Защита от циклов (на всякий случай) через visited.
    """
    by_parent: dict[int, list[int]] = defaultdict(list)
    for cat in categories:
        if cat.parent_id:
            by_parent[cat.parent_id].append(cat.pk)

    result: set[int] = set()
    stack = [root_id]
    while stack:
        current = stack.pop()
        if current in result:
            continue
        result.add(current)
        stack.extend(by_parent.get(current, []))

    return result


# ============================================================================
# CRUD бюджета
# ============================================================================
@extend_schema(tags=["Budget"])
class BudgetListCreateView(generics.ListCreateAPIView):
    """Список бюджетов пользователя + создание."""

    serializer_class = BudgetSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self):
        qs = Budget.objects.filter(user=self.request.user).select_related("category")
        period_type = self.request.query_params.get("period_type")
        if period_type in dict(Budget.PERIOD_CHOICES):
            qs = qs.filter(period_type=period_type)
        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=["Budget"])
class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Чтение/редактирование/удаление одного бюджета."""

    serializer_class = BudgetSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["get", "patch", "put", "delete"]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related("category")


# ============================================================================
# Сводка бюджета на период
# ============================================================================
@extend_schema(
    tags=["Budget"],
    parameters=[
        OpenApiParameter(
            name="period_type",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
        ),
        OpenApiParameter(
            name="date", type=str, location=OpenApiParameter.QUERY, required=False
        ),
    ],
)
class BudgetSummaryView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get(self, request):
        user = request.user

        # --- Период ---
        period_type = request.query_params.get("period_type") or Budget.PERIOD_MONTHLY
        if period_type not in dict(Budget.PERIOD_CHOICES):
            period_type = Budget.PERIOD_MONTHLY

        try:
            reference = (
                date.fromisoformat(request.query_params["date"])
                if request.query_params.get("date")
                else date.today()
            )
        except (ValueError, KeyError):
            reference = date.today()

        period_start, period_end = _period_bounds(period_type, reference)
        start_dt, end_dt = _to_aware_range(period_start, period_end)

        # --- Все бюджеты пользователя на период ---
        budgets = list(
            Budget.objects.filter(
                user=user,
                period_type=period_type,
                is_active=True,
            ).select_related("category")
        )

        # --- Сумма ВСЕХ расходов за период (для общего бюджета) ---
        total_expense = Transaction.objects.filter(
            user=user,
            create_at__gte=start_dt,
            create_at__lte=end_dt,
            category__type_transaction="expense",
        ).aggregate(total=Sum("amount"))["total"] or Decimal(0)

        # --- Разбиваем бюджеты: общий и категорийные ---
        total_budget = next((b for b in budgets if b.category_id is None), None)
        category_budgets = [b for b in budgets if b.category_id is not None]

        # --- Общий бюджет ---
        total_budget_resp = None
        if total_budget is not None:
            limit = total_budget.amount or Decimal(0)
            remaining = limit - total_expense
            percent = float(total_expense / limit * 100) if limit > 0 else 0.0
            total_budget_resp = {
                "id": total_budget.pk,
                "amount": float(limit),
                "spent": float(total_expense),
                "remaining": float(remaining),
                "percent": round(percent, 1),
                "is_exceeded": remaining < 0,
            }

        # --- Категорийные ---
        categories = list(Category.objects.filter(user=user))
        per_category = (
            Transaction.objects.filter(
                user=user,
                create_at__gte=start_dt,
                create_at__lte=end_dt,
                category__type_transaction="expense",
            )
            .values("category_id")
            .annotate(total=Sum("amount"))
        )
        spent_by_category = {
            row["category_id"]: (row["total"] or Decimal(0)) for row in per_category
        }

        result_budgets = []
        total_limit = Decimal(0)
        total_spent = Decimal(0)

        for budget in category_budgets:
            descendant_ids = _collect_descendant_ids(categories, budget.category_id)
            spent = sum(
                (spent_by_category.get(cid, Decimal(0)) for cid in descendant_ids),
                Decimal(0),
            )
            limit = budget.amount or Decimal(0)
            remaining = limit - spent
            percent = float(spent / limit * 100) if limit > 0 else 0.0

            result_budgets.append(
                {
                    "id": budget.pk,
                    "category": {
                        "id": budget.category_id,
                        "name": budget.category.name,
                    },
                    "period_type": budget.period_type,
                    "amount": float(limit),
                    "spent": float(spent),
                    "remaining": float(remaining),
                    "percent": round(percent, 1),
                    "is_exceeded": remaining < 0,
                }
            )

            total_limit += limit
            total_spent += spent

        result_budgets.sort(
            key=lambda b: (-b["percent"], b["category"]["name"]),
        )

        return Response(
            {
                "period": {
                    "type": period_type,
                    "start": period_start.isoformat(),
                    "end": period_end.isoformat(),
                },
                "total_budget": total_budget_resp,  # ← общий (может быть null)
                "totals": {
                    # Суммы только по категорийным (без общего, чтобы не двоить)
                    "limit": float(total_limit),
                    "spent": float(total_spent),
                    "remaining": float(total_limit - total_spent),
                    "percent": round(
                        float(total_spent / total_limit * 100)
                        if total_limit > 0
                        else 0.0,
                        1,
                    ),
                    "total_expense": float(
                        total_expense
                    ),  # расходы за период (для справки)
                },
                "budgets": result_budgets,
            }
        )
