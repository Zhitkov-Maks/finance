from datetime import date

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FinancialGoal, Insight, InsightSettings
from .serializers import (
    FinancialGoalSerializer,
    InsightSerializer,
    InsightSettingsSerializer,
)


@extend_schema(tags=["Insights"])
class InsightListView(generics.ListAPIView):
    serializer_class = InsightSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self):
        qs = Insight.objects.filter(user=self.request.user)
        if self.request.query_params.get("active") == "1":
            qs = qs.filter(is_dismissed=False)
        return qs.order_by("-created_at")


@extend_schema(tags=["Insights"])
class InsightDismissView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def post(self, request, pk):
        Insight.objects.filter(user=request.user, pk=pk).update(is_dismissed=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GoalCurrentView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        today = date.today()
        month_start = today.replace(day=1)
        goal = FinancialGoal.objects.filter(
            user=request.user, month=month_start
        ).first()

        if not goal:
            return Response({"goal": None})

        serializer = FinancialGoalSerializer(goal)
        return Response({"goal": serializer.data})

    def post(self, request):
        today = date.today()
        month_start = today.replace(day=1)

        # Ищем, есть ли уже цель на этот месяц
        goal = FinancialGoal.objects.filter(
            user=request.user, month=month_start
        ).first()

        if goal:
            # Если есть, обновляем
            serializer = FinancialGoalSerializer(goal, data=request.data, partial=True)
        else:
            # Если нет, создаем (month устанавливаем принудительно)
            data = request.data.copy()
            data["month"] = month_start
            serializer = FinancialGoalSerializer(data=data)

        if serializer.is_valid():
            # Если тип 'limit' и категория не выбрана - это лимит на ВСЕ расходы
            serializer.save(user=request.user, month=month_start)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        today = date.today()
        month_start = today.replace(day=1)
        FinancialGoal.objects.filter(user=request.user, month=month_start).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Insights"])
class InsightSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = InsightSettingsSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_object(self):
        settings, _ = InsightSettings.objects.get_or_create(user=self.request.user)
        return settings
