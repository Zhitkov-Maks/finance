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
        fields = ["id", "name", "balance", "is_active"]


class AccountTransactionSerializer(serializers.ModelSerializer):
    """
    Нужен для отображения доходов при получении детальной
    информации о конкретном счете.
    """

    class Meta:
        model = Transaction
        fields = ["id", "amount", "create_at", "is_active"]


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


class BalanceHistoryQuerySerializer(serializers.Serializer):
    """
    Сериализатор для валидации query-параметров эндпоинта
    /accounts/balance-history.
    """

    date_from = serializers.DateField(required=True)
    date_to = serializers.DateField(required=True)
    account_id = serializers.IntegerField(required=False, allow_null=True)
    include_inactive = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        if attrs["date_from"] > attrs["date_to"]:
            raise serializers.ValidationError("date_from не может быть больше date_to")
        # Ограничим максимальный период — полгода
        delta = (attrs["date_to"] - attrs["date_from"]).days
        if delta > 366:
            raise serializers.ValidationError("Максимальный период — 366 дней")
        return attrs


class BalanceHistoryAccountSerializer(serializers.Serializer):
    """Информация о счёте в ответе."""

    id = serializers.IntegerField()
    name = serializers.CharField()


class BalanceHistoryPointSerializer(serializers.Serializer):
    """Одна точка на графике."""

    date = serializers.DateField()
    accounts = serializers.DictField(
        child=serializers.FloatField(),
        help_text="Словарь account_id -> баланс на дату",
    )
    total = serializers.FloatField()


class BalanceHistoryResponseSerializer(serializers.Serializer):
    """Полный ответ эндпоинта."""

    accounts = BalanceHistoryAccountSerializer(many=True)
    results = BalanceHistoryPointSerializer(many=True)
