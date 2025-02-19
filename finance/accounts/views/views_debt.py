from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.authentication import (
    TokenAuthentication,
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated

from accounts.models import Transfer, Debt
from accounts.serializers.serializers_debt import (
    ReadDebtSerializer,
    CreateDebtSerializer,
)


class DebtsViewSet(viewsets.ModelViewSet):
    serializer_class = ReadDebtSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateDebtSerializer
        return ReadDebtSerializer

    def get_queryset(self) -> QuerySet:
        return Debt.objects.select_related(
            "transfer", "transfer__source_account", "transfer__destination_account"
        ).filter(user=self.request.user.pk)

    def perform_create(self, serializer):
        data = self.request.data

        # Создание нового перевода (долга)
        transfer = Transfer.objects.create(
            source_account_id=data["source_account"],
            destination_account_id=data["destination_account"],
            amount=data["amount"],
            timestamp=data["timestamp"],
        )

        serializer.save(
            transfer=transfer, borrower_description=data["borrower_description"]
        )
