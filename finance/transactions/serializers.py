from rest_framework import serializers
from django.db import models

from .models import Transaction, Category
from accounts.serializers import AccountSerializer


class ParentSerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class CategorySerializer(serializers.ModelSerializer):
    """
    Нужен для сериализации категорий доходов.
    """
    has_children = serializers.BooleanField(read_only=True)
    children = ParentSerializers(many=True, source='get_children_direct')

    class Meta:
        model = Category
        fields = ["id", "name", "children", "has_children", "type_transaction"]


class CategoryIDSerializers(serializers.ModelSerializer):
    children = ParentSerializers(many=True, source='get_children_direct')

    class Meta:
        model = Category
        fields = ["id", "name", "children"]


class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Нужен для сериализации категорий доходов.
    """

    class Meta:
        model = Category
        fields = ["id", "name", "parent"]


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


class ChildCategorySerializer(serializers.Serializer):
    """Сериализатор для дочерней категории"""
    name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class CategoryTransactionStatisticsSerializer(serializers.Serializer):
    """Сериализатор для статистики по категориям"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    children = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        default=list
    )
    parent = serializers.DictField(required=False, allow_null=True)


class StatisticsResponseSerializer(serializers.Serializer):
    """
    Сериализатор для общего ответа со статистикой расходов.
    """
    statistics = CategoryTransactionStatisticsSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
