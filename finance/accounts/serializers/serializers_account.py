from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from expenses.models import Expense
from incomes.models import Income
from accounts.models import Account


class BaseAccountSerializer(serializers.ModelSerializer):
    """
    Базовый класс для сериализации счетов. Предназначен для переиспользования.
    """
    class Meta:
        model = Account
        fields = ["id", "name", "balance"]


class AccountIncomeSerializer(serializers.ModelSerializer):
    """
    Нужен для отображения доходов при получении детальной информации о конкретном счете.
    """
    class Meta:
        model = Income
        fields = ["id", "amount", "create_at"]


class AccountExpenseSerializer(serializers.ModelSerializer):
    """
    Нужен для отображения расходов при получении детальной информации о конкретном счете.
    """
    class Meta:
        model = Expense
        fields = ["id", "amount", "create_at"]



class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'balance', 'is_active']


class AccountListResponseSerializer(serializers.Serializer):
    """
    Сериализатор для отображения списка счетов с общим балансом.
    """
    accounts = serializers.ListField(child=AccountSerializer())
    total_balance = serializers.DecimalField(max_digits=10, decimal_places=2)


class AccountSerializerDetail(serializers.ModelSerializer):
    """
    Нужен для получения детальной информации о счете, которая будет включать в себя
    и информация о доходах и расходах по данному счету за последний месяц.
    """
    incomes = serializers.SerializerMethodField()
    expenses = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ["id", "name", "balance", "is_active", "incomes", "expenses"]

    @extend_schema_field(AccountIncomeSerializer(many=True))
    def get_incomes(self, obj):
        incomes_queryset = obj.incomes.order_by('-create_at')[:10]
        return AccountIncomeSerializer(incomes_queryset, many=True).data

    @extend_schema_field(AccountExpenseSerializer(many=True))
    def get_expenses(self, obj):
        expenses_queryset = obj.expenses.order_by('-create_at')[:10]
        return AccountExpenseSerializer(expenses_queryset, many=True).data


class AccountPutSerializer(BaseAccountSerializer):
    """
    Нужен для полного редактирования счета.
    """
    class Meta(BaseAccountSerializer.Meta):
        fields = ["name", "balance"]


class AccountGetSerializer(BaseAccountSerializer):
    """
    Нужен для полного редактирования счета.
    """
    class Meta(BaseAccountSerializer.Meta):
        fields = ["id", "name", "balance"]


class AccountPatchSerializer(BaseAccountSerializer):
    """
    Нужен для частичного редактирования.
    """
    class Meta(BaseAccountSerializer.Meta):
        fields = ["balance"]


class AccountToggleStatusSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации о счете после переключения активности.
    """
    class Meta:
        model = Account
        fields = ['is_active']
