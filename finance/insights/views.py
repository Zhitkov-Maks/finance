from datetime import date, datetime

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

    def _parse_month(self, request):
        month_str = request.query_params.get("month") or request.data.get("month")
        if month_str:
            try:
                return datetime.strptime(month_str, "%Y-%m-%d").date().replace(day=1)
            except (ValueError, TypeError):
                pass
        return date.today().replace(day=1)

    def _is_motivation(self, request):
        goal_type = request.query_params.get("goal_type") or request.data.get(
            "goal_type"
        )
        return goal_type == FinancialGoal.GOAL_MOTIVATION

    def get(self, request):
        month_start = self._parse_month(request)
        is_motivation = self._is_motivation(request)

        goal = FinancialGoal.objects.filter(
            user=request.user,
            month=month_start,
            is_motivation_goal=is_motivation,
        ).first()

        if not goal:
            return Response({"goal": None})

        return Response({"goal": FinancialGoalSerializer(goal).data})

    def post(self, request):
        month_start = self._parse_month(request)
        goal_type = request.data.get("goal_type")

        if goal_type not in dict(FinancialGoal.GOAL_TYPES):
            return Response(
                {"detail": "Некорректный goal_type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_motivation = goal_type == FinancialGoal.GOAL_MOTIVATION

        goal = FinancialGoal.objects.filter(
            user=request.user,
            month=month_start,
            is_motivation_goal=is_motivation,
        ).first()

        data = request.data.copy()
        data["is_motivation_goal"] = is_motivation

        if goal:
            serializer = FinancialGoalSerializer(goal, data=data, partial=True)
        else:
            serializer = FinancialGoalSerializer(data=data)

        if serializer.is_valid():
            serializer.save(
                user=request.user,
                month=month_start,
                is_motivation_goal=is_motivation,  # ← явно
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        month_start = self._parse_month(request)
        is_motivation = self._is_motivation(request)

        FinancialGoal.objects.filter(
            user=request.user,
            month=month_start,
            is_motivation_goal=is_motivation,
        ).delete()

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
