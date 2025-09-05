from rest_framework import serializers

from transactions.models import Transaction
from accounts.models import Account


class BaseAccountSerializer(serializers.ModelSerializer):
    """
    Базовый класс для сериализации счетов.
    Предназначен для переиспользования.
    """

    class Meta:
        model = Account
        fields = ["id", "name", "balance"]


class AccountTransactionSerializer(serializers.ModelSerializer):
    """
    Нужен для отображения доходов при получении детальной
    информации о конкретном счете.
    """

    class Meta:
        model = Transaction
        fields = ["id", "amount", "create_at"]


class AccountSerializer(serializers.ModelSerializer):
    """Нужен для базовой работы со счетами."""

    class Meta:
        model = Account
        fields = ['id', 'name', 'balance', 'is_active']


class AccountListResponseSerializer(serializers.Serializer):
    """Сериализатор для отображения списка счетов с общим балансом."""

    accounts = serializers.ListField(child=AccountSerializer())
    total_balance = serializers.DecimalField(max_digits=10, decimal_places=2)


class AccountPutSerializer(BaseAccountSerializer):
    """Нужен для полного редактирования счета."""

    class Meta(BaseAccountSerializer.Meta):
        fields = ["name", "balance"]


class AccountGetSerializer(BaseAccountSerializer):
    """Нужен для полного редактирования счета."""

    class Meta(BaseAccountSerializer.Meta):
        fields = ["id", "name", "balance"]


class AccountPatchSerializer(BaseAccountSerializer):
    """Нужен для частичного редактирования."""

    class Meta(BaseAccountSerializer.Meta):
        fields = ["balance"]


class AccountToggleStatusSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации о счете
    после переключения активности.
    """

    class Meta:
        model = Account
        fields = ['is_active']
