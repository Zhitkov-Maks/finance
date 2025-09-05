from rest_framework import serializers

from .models import Transaction, Category
from accounts.serializers import AccountSerializer


class CategorySerializer(serializers.ModelSerializer):
    """
    Нужен для сериализации категорий доходов.
    """

    class Meta:
        model = Category
        fields = ["id", "name"]


class TransactionSerializer(serializers.ModelSerializer):
    """
    Нужен для сериализации доходов.
    """

    category = CategorySerializer()
    account = AccountSerializer()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "amount",
            "create_at",
            "category",
            "account",
            "comment"
        ]


class TransactionSerializersAdd(serializers.ModelSerializer):
    """
    Нужен для сериализации входных данных для добавления дохода.
    """
    class Meta:
        model = Transaction
        fields = [
            "id",
            "amount",
            "create_at",
            "category",
            "account",
            "comment"
        ]


class TransactionSerializerGet(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    account = AccountSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "amount",
            "create_at",
            "category",
            "account",
            "comment"
        ]


class TransactionSerializersPatch(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ["amount"]


class CategoryTransactionStatisticsSerializer(serializers.Serializer):
    """
    Нужен для показа статистики доходов по месяцам.
    """

    category_name = serializers.CharField(source="category__name")
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class StatisticsResponseSerializer(serializers.Serializer):
    """
    Сериализатор для общего ответа со статистикой расходов.
    """
    statistics = CategoryTransactionStatisticsSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
