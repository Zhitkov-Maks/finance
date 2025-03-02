import decimal

from rest_framework import serializers

from accounts.models import Transfer, Account


class TransferSerializer(serializers.ModelSerializer):
    """
    Нужен для сериализации и валидации данных для работы с переводами
    между своими счетами.
    """

    class Meta:
        model = Transfer
        fields = [
            "source_account",
            "destination_account",
            "amount",
            "timestamp"
        ]

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
                "Insufficient balance in the source account."
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
