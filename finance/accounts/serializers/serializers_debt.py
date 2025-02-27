from rest_framework import serializers

from accounts.models import Debt, Transfer, Account


class DebtCreateSerializer(serializers.Serializer):
    """Нужен для работы с созданием долга."""

    account_id = serializers.IntegerField()
    type = serializers.CharField(max_length=10)  # debt или lend
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(max_length=100)
    date = serializers.DateField()


class DebtRepaymentSerializer(serializers.Serializer):
    """Нужен для работы с возвратом долгов."""

    debt_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    type = serializers.CharField(max_length=10)


class TransferSerializer(serializers.ModelSerializer):
    """Нужен при работе со списком долгов."""

    class Meta:
        model = Transfer
        fields = [
            'amount',
            'timestamp'
        ]

class DebtListSerializer(serializers.ModelSerializer):
    """Нужен для получения списка долгов."""

    transfer = TransferSerializer()
    class Meta:
        model = Debt
        fields = ['id', 'transfer', 'borrower_description']


class AccountSerializer(serializers.ModelSerializer):
    """
    Нужен для показа полной информации о счетах при работе с
    конкретным долгом.
    """

    class Meta:
        model = Account
        fields = ['id', 'name', 'balance', 'user']


class TransferDetailSerializer(serializers.ModelSerializer):
    """
    Нужен для отображения информации о переводах, требуется в
    сериализаторе получения полной информации о долге.
    """

    source_account = AccountSerializer()
    destination_account = AccountSerializer()

    class Meta:
        model = Transfer
        fields = [
            'id',
            'source_account',
            'destination_account',
            'amount',
            'timestamp'
        ]

class DebtDetailSerializer(serializers.ModelSerializer):
    """Показ полной информации о конкретном долге."""

    transfer = TransferDetailSerializer()
    class Meta:
        model = Debt
        fields = ['id', 'transfer', 'borrower_description']


class SuccessSerializer(serializers.Serializer):
    """
    Нужен при создании счетов, для уведомления об успешной
    выполненной операции.
    """

    status = serializers.CharField(max_length=10)
    message = serializers.CharField(max_length=1000)
