from rest_framework import serializers

from accounts.serialisers import AccountSerializer
from .models import Expense, Category


class CategorySerializerExpenses(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ExpenseSerializer(serializers.ModelSerializer):
    category = CategorySerializerExpenses(read_only=True)
    account = AccountSerializer(read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'amount', "create_at", "category", "account"]


class BaseSerializerExpenses(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['id', 'amount', "create_at", "category", "account"]


class ExpenseSerializersAdd(BaseSerializerExpenses):
    class Meta(BaseSerializerExpenses.Meta):
        fields = BaseSerializerExpenses.Meta.fields


class ExpenseSerializersPut(BaseSerializerExpenses):
    class Meta(BaseSerializerExpenses.Meta):
        fields = ["amount", "category", "account", "create_at"]


class ExpenseSerializersPatch(BaseSerializerExpenses):
    class Meta(BaseSerializerExpenses.Meta):
        fields = ["amount"]


class CategoryExpenseStatisticsSerializer(serializers.Serializer):
    category_name = serializers.CharField(source='category__name')
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
