import decimal

from rest_framework import serializers

from accounts.models import Account
from .models import Transfer


class TransferSerializer(serializers.ModelSerializer):
    """
    Нужен для сериализации и валидации данных для работы с переводами
    между своими счетами.
    """
    source_account_name = serializers.CharField(
        source='source_account.name', read_only=True
    )
    destination_account_name = serializers.CharField(
        source='destination_account.name', read_only=True
    )

    class Meta:
        model = Transfer
        fields = [
            "source_account",
            "source_account_name",
            "destination_account", 
            "destination_account_name",
            "amount",
            "timestamp"
        ]
        extra_kwargs = {
            'source_account': {'write_only': True},
            'destination_account': {'write_only': True}
        }

    def validate(self, attrs):
        """
        Дополнительная валидация счетов при переводе денег
        между своими счетами.
        """

        source_account: Account = attrs.get("source_account")
        destination_account: Account = attrs.get("destination_account")
        amount: decimal = attrs.get("amount")

        # Validate that source and destination accounts are different
        if source_account == destination_account:
            raise serializers.ValidationError(
                "Source and destination accounts must be different."
            )

        # Validate that the source account has sufficient balance
        if amount and source_account.balance < amount:
            raise serializers.ValidationError(
                "Недостаточно средств на счете."
            )

        return attrs


class IsNotAuthentication(serializers.Serializer):
    """Нужен для отображения в openapi на указание ошибки аутентификации."""

    detail = serializers.CharField()


class ValidationError(serializers.Serializer):
    """
     Нужен для отображения в openapi на указание ошибки
     переданного значения.
    """

    detail = serializers.ListField(child=serializers.CharField())


class NotFoundError(serializers.Serializer):
    """
     Нужен для отображения в openapi на указание ошибки получения
     счета по ID.
    """

    detail = serializers.CharField()


class TransferResponseSerializer(serializers.Serializer):
    """
    Нужен для сериализации и валидации данных для работы с переводами
    между своими счетами.
    """
    class Meta:
        model = Transfer
        fields = [
            'id',
            'source_account',
            'destination_account',
            'amount',
            'timestamp'
        ]
