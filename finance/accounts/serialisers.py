from datetime import timedelta

from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from expenses.models import Expense
from incomes.models import Income
from .models import Account


class BaseAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "balance"]


class AccountIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ["id", "amount", "create_at"]


class AccountExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "amount", "create_at"]


class AccountSerializer(BaseAccountSerializer):
    class Meta(BaseAccountSerializer.Meta):
        pass


class AccountSerializerDetail(serializers.ModelSerializer):
    incomes = serializers.SerializerMethodField()
    expenses = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ["id", "name", "balance", "incomes", "expenses"]

    @extend_schema_field(AccountIncomeSerializer(many=True))
    def get_incomes(self, obj):
        two_weeks_ago = timezone.now() - timedelta(days=30)
        incomes_queryset = obj.incomes.filter(create_at__gte=two_weeks_ago)
        return AccountIncomeSerializer(incomes_queryset, many=True).data

    @extend_schema_field(AccountIncomeSerializer(many=True))
    def get_expenses(self, obj):
        two_weeks_ago = timezone.now() - timedelta(days=30)
        expenses_queryset = obj.expenses.filter(create_at__gte=two_weeks_ago)
        return AccountExpenseSerializer(expenses_queryset, many=True).data


class AccountPutSerializer(BaseAccountSerializer):
    class Meta(BaseAccountSerializer.Meta):
        fields = ["name", "balance"]


class AccountPatchSerializer(BaseAccountSerializer):
    class Meta(BaseAccountSerializer.Meta):
        fields = ["balance"]
