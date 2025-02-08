from rest_framework import serializers

from .models import Income, Category
from accounts.serializers.serializers_account import AccountSerializer


class CategorySerializer(serializers.ModelSerializer):
    """
    Нужен для сериализации категорий доходов.
    """

    class Meta:
        model = Category
        fields = ["id", "name"]


class IncomeSerializer(serializers.ModelSerializer):
    """
    Нужен для сериализации доходов.
    """

    category = CategorySerializer()
    account = AccountSerializer()

    class Meta:
        model = Income
        fields = ["id", "amount", "create_at", "category", "account"]


class IncomeSerializersAdd(serializers.ModelSerializer):
    """
    Нужен для сериализации входных данных для добавления дохода.
    """
    class Meta:
        model = Income
        fields = ["id", "amount", "create_at", "category", "account"]


class IncomeSerializerGet(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    account = AccountSerializer(read_only=True)
    class Meta:
        model = Income
        fields = ["id", "amount", "create_at", "category", "account"]


class IncomeSerializersPatch(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ["amount"]


class CategoryIncomeStatisticsSerializer(serializers.Serializer):
    """
    Нужен для показа статистики доходов по месяцам.
    """

    category_name = serializers.CharField(source="category__name")
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class StatisticsResponseSerializer(serializers.Serializer):
    """
    Сериализатор для общего ответа со статистикой расходов.
    """
    statistics = CategoryIncomeStatisticsSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)