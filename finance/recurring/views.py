from datetime import date, timedelta

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RecurringTransaction
from .serializers import RecurringTransactionSerializer, UpcomingPaymentSerializer


@extend_schema(tags=["Recurring"])
class RecurringListCreateView(generics.ListCreateAPIView):
    serializer_class = RecurringTransactionSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self):
        return (
            RecurringTransaction.objects.filter(user=self.request.user)
            .select_related("category", "account")
            .order_by("next_run_date")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=["Recurring"])
class RecurringDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecurringTransactionSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["get", "patch", "put", "delete"]

    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user)


@extend_schema(tags=["Recurring"])
class UpcomingPaymentsView(APIView):
    """
    Возвращает список будущих платежей на указанное количество дней вперед.
    По умолчанию — на 30 дней.
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get(self, request):
        try:
            days = int(request.query_params.get("days", 30))
        except ValueError:
            days = 30

        today = date.today()
        end_period = today + timedelta(days=days)

        recs = RecurringTransaction.objects.filter(
            user=request.user, is_active=True
        ).select_related("category", "account")

        result = []

        for rec in recs:
            # Начинаем либо с сегодня, либо с next_run_date (что позже)
            curr_date = max(rec.next_run_date, today)

            # Если у операции есть end_date, ограничиваем
            max_date = min(end_period, rec.end_date) if rec.end_date else end_period

            while curr_date <= max_date:
                result.append(
                    {
                        "id": rec.id,
                        "title": rec.title,
                        "amount": rec.amount,
                        "type_transaction": rec.type_transaction,
                        "category_name": rec.category.name,
                        "account_name": rec.account.name,
                        "date": curr_date,
                    }
                )
                curr_date = rec.calculate_next_run(curr_date)

        # Сортируем по дате
        result.sort(key=lambda x: (x["date"], x["title"]))

        serializer = UpcomingPaymentSerializer(result, many=True)
        return Response(serializer.data)
