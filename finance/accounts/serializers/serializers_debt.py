from rest_framework import serializers

from accounts.models import Debt


class ReadDebtSerializer(serializers.ModelSerializer):
    transfer_amount = serializers.ReadOnlyField(source="transfer.amount")
    transfer_source_account = serializers.ReadOnlyField(
        source="transfer.source_account.name"
    )
    transfer_destination_account = serializers.ReadOnlyField(
        source="transfer.destination_account.name"
    )
    transfer_timestamp = serializers.ReadOnlyField(source="transfer.timestamp")

    class Meta:
        model = Debt
        fields = [
            "id",
            "borrower_description",
            "transfer_amount",
            "transfer_source_account",
            "transfer_destination_account",
            "transfer_timestamp",
        ]


class CreateDebtSerializer(serializers.ModelSerializer):
    source_account = serializers.IntegerField()
    destination_account = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    timestamp = serializers.DateTimeField()

    class Meta:
        model = Debt
        fields = [
            "borrower_description",
            "amount",
            "source_account",
            "destination_account",
            "timestamp",
        ]
