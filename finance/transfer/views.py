import decimal

from django.db.models import QuerySet, Q
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.authentication import (
    TokenAuthentication,
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Account
from .schemas import (
    TransferSchema,
    TransferHistoryViewSchema,
    TransferRetrieveViewSchema,
)
from .models import Transfer
from .serializers import TransferSerializer
from app_user.models import CustomUser


@extend_schema(tags=["Transfer"])
@TransferSchema
class TransferFundsView(generics.CreateAPIView):
    """
    Класс для создания нового перевода между своими счетами.
    """

    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def perform_create(self, serializer):
        """
        Переопределяем метод для перевода баланса между счетами.
        """
        source_account: Account = serializer.validated_data["source_account"]
        destination_account: Account = serializer.validated_data[
            "destination_account"
        ]
        amount: decimal = serializer.validated_data["amount"]

        source_account.balance -= amount
        destination_account.balance += amount

        source_account.save()
        destination_account.save()

        transfer = serializer.save()
        return transfer

    def post(self, request, *args, **kwargs):
        """
        Переопределяем метод для вызова валидации,
        сохранения и возврата ответа.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransferPagination(PageNumberPagination):
    """
    Класс для создания пагинации.
    """

    page_size: int = 10
    page_size_query_param: str = "page_size"
    max_page_size: int = 100


@extend_schema(tags=["Transfer"])
@TransferHistoryViewSchema
class TransferHistoryView(generics.ListAPIView):
    """
    Класс для получения списка переводов между счетами.
    """

    pagination_class = TransferPagination
    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self) -> QuerySet:
        """
        Переопределяем, чтобы вернуть данные по конкретному пользователю.
        """
        user: CustomUser = self.request.user
        return Transfer.objects.filter(
            Q(source_account__user=user) | Q(destination_account__user=user),
            source_account__is_system_account=False,
            destination_account__is_system_account=False
        ).order_by("-timestamp")


@extend_schema(tags=["Transfer"])
@TransferRetrieveViewSchema
class TransferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Класс для редактирования удаления и получения подробной
    информации о переводе.
    """

    serializer_class = TransferSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names: list = ["get", "put", "delete"]

    def get_queryset(self) -> QuerySet:
        user: CustomUser = self.request.user
        return (
            Transfer.objects.filter(source_account__user=user)
            .union(Transfer.objects.filter(destination_account__user=user))
            .order_by("-timestamp")
        )

    def perform_update(self, serializer):
        """
        Изменяем балансы счетов при редактировании.
        :param serializer: Сериализатор для обновления.
        """
        transfer: Transfer = self.get_object()

        old_amount: decimal = transfer.amount
        new_amount: decimal = serializer.validated_data["amount"]

        source_account: Account = transfer.source_account
        destination_account: Account = transfer.destination_account

        if new_amount != old_amount:
            source_account.balance += old_amount - new_amount
            destination_account.balance -= old_amount - new_amount

            source_account.save()
            destination_account.save()
        serializer.save()

    def perform_destroy(self, instance):
        """
        Откат баланса счетов при удалении перевода.
        :param instance: Объект Transfer
        """
        source_account: Account = instance.source_account
        destination_account: Account = instance.destination_account

        source_account.balance += instance.amount
        destination_account.balance -= instance.amount

        source_account.save()
        destination_account.save()
        instance.delete()
