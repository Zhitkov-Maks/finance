from datetime import date
from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers
from transactions.models import Transaction

from .models import FinancialGoal, Insight, InsightSettings


class InsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insight
        fields = (
            "id",
            "insight_type",
            "severity",
            "title",
            "message",
            "data",
            "action_url",
            "is_dismissed",
            "is_read",
            "created_at",
        )
        read_only_fields = fields


class FinancialGoalSerializer(serializers.ModelSerializer):
    current = serializers.SerializerMethodField()
    percent = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = FinancialGoal
        fields = (
            "id",
            "goal_type",
            "amount",
            "category",
            "category_name",
            "month",
            "current",
            "percent",
        )
        read_only_fields = ("id", "month")

    def get_current(self, obj):
        today = date.today()
        month_start = obj.month

        if obj.goal_type == FinancialGoal.GOAL_SAVE:
            inc = Transaction.objects.filter(
                user=obj.user,
                category__type_transaction="income",
                create_at__date__gte=month_start,
                create_at__date__lte=today,
            ).aggregate(s=Sum("amount"))["s"] or Decimal(0)
            exp = Transaction.objects.filter(
                user=obj.user,
                category__type_transaction="expense",
                create_at__date__gte=month_start,
                create_at__date__lte=today,
            ).aggregate(s=Sum("amount"))["s"] or Decimal(0)
            return float(inc - exp)
        else:
            qs = Transaction.objects.filter(
                user=obj.user,
                category__type_transaction="expense",
                create_at__date__gte=month_start,
                create_at__date__lte=today,
            )
            if obj.category:
                qs = qs.filter(category=obj.category)
            spent = qs.aggregate(s=Sum("amount"))["s"] or Decimal(0)
            return float(spent)

    def get_percent(self, obj):
        current = self.get_current(obj)
        if obj.amount <= 0:
            return 0
        percent = (current / float(obj.amount)) * 100
        # Для Save: прогресс не может быть больше 100 (если сэкономили больше цели - молодцы)
        # Для Limit: если превысили - покажем >100 (например, 120%)
        if obj.goal_type == FinancialGoal.GOAL_SAVE:
            return round(min(100, max(0, percent)), 1)
        return round(max(0, percent), 1)


class InsightSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsightSettings
        fields = ("small_expense_threshold", "idle_cash_threshold")
