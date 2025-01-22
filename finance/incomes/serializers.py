from rest_framework import serializers

from .models import Income, Category
from accounts.serialisers import AccountSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class IncomeSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    account = AccountSerializer(read_only=True)
    class Meta:
        model = Income
        fields = ['id', 'amount', "create_at", "category", "account"]


class IncomeSerializersAdd(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ['id', 'amount', "create_at", "category", "account"]
