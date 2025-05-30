from rest_framework import serializers

from accounts.serializers import AccountSerializer
from .models import Expense, Category


class CategorySerializerExpenses(serializers.ModelSerializer):
    """
    Нужен для сериализации категорий расходов.
    """

    class Meta:
        model = Category
        fields = ["id", "name"]


class ExpenseSerializer(serializers.ModelSerializer):
    """
    Нужен для сериализации списка расходов.
    """

    category = CategorySerializerExpenses(read_only=True)
    account = AccountSerializer(read_only=True)

    class Meta:
        model = Expense
        fields = ["id", "amount", "create_at", "category", "account", "comment"]


class BaseSerializerExpenses(serializers.ModelSerializer):
    """
    Класс для переиспользования при редактировании.(Изменить количество полей).
    """

    class Meta:
        model = Expense
        fields = ["id", "amount", "create_at", "category", "account", "comment"]


class ExpenseSerializersAdd(BaseSerializerExpenses):
    """
    Нужен для получения данных при создании расхода.
    """

    class Meta:
        model = Expense
        fields = ["id", "amount", "create_at", "category", "account", "comment"]


class ExpenseSerializersPut(BaseSerializerExpenses):
    """
    Нужен для полного редактирования расходов.
    """

    class Meta(BaseSerializerExpenses.Meta):
        fields = ["amount", "category", "account", "create_at", "comment"]


class ExpenseSerializersPatch(BaseSerializerExpenses):
    """
    Нужен для частичного редактирования расходов.
    """

    class Meta(BaseSerializerExpenses.Meta):
        fields = ["amount"]


class CategoryExpenseStatisticsSerializer(serializers.Serializer):
    """
    Нужен для показа статистики расходов по месяцам.
    """

    category_name = serializers.CharField(source="category__name")
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class StatisticsResponseSerializer(serializers.Serializer):
    """
    Сериализатор для общего ответа со статистикой расходов.
    """
    statistics = CategoryExpenseStatisticsSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
