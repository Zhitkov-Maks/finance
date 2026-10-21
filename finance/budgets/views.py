from datetime import date

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

from .models import Budget
from .serializers import BudgetSerializer
from .services import compute_budget_summary


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

        return Response(compute_budget_summary(user, period_type, reference))
