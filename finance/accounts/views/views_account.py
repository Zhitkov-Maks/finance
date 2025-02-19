from django.db.models import QuerySet, Sum
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.authentication import (
    TokenAuthentication,
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Account
from accounts.schemas import (
    listAccountSchema,
    RetrieveUpdateDeleteAccountSchema
)
from accounts.serializers.serializers_account import (
    AccountSerializer,
    AccountSerializerDetail,
    AccountToggleStatusSerializer,
    AccountGetSerializer,
)


class AccountPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=["Accounts"])
@listAccountSchema
class ListAccounts(generics.ListCreateAPIView):
    """
    Класс для получения списка счетов или создания нового счета пользователя.
    """

    pagination_class = AccountPagination
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AccountGetSerializer
        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        """
        Переопределил метод для показа счетов только конкретного пользователя.
        :return Queryset: Список счетов пользователя.
        """
        return Account.objects.filter(user=self.request.user.pk).order_by("-balance")

    def perform_create(self, serializer):
        """
        Метод переопределяется, чтобы включить текущего пользователя
        в качестве дополнительного аргумента при сохранении сериализатора
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def list(self, request, *args, **kwargs):
        """
        Переопределяем метод list для добавления общего баланса счетов в ответ.
        """
        queryset = self.get_queryset()

        # Calculate total balance across all accounts once
        total_balance = queryset.filter(is_active=True).aggregate(total=Sum("balance"))["total"] or 0

        # Paginate the queryset using DRF's pagination class
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                [
                    {
                        "accounts": serializer.data,
                        "total_balance": total_balance,
                    }
                ]
            )

        # Fallback if pagination is not used (not typical)
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            [
                {
                    "accounts": serializer.data,
                    "total_balance": total_balance,
                }
            ]
        )


@extend_schema(tags=["Accounts"])
@RetrieveUpdateDeleteAccountSchema
class RetrieveUpdateDeleteAccount(generics.RetrieveUpdateDestroyAPIView):
    """
    Класс для редактирования, удаления и просмотра конкретного счета.
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_serializer_class(self):
        """
        Переопределен метод для выбора сериализатора в зависимости от запроса.
        """
        if self.request.method == "GET":
            return AccountSerializerDetail
        return AccountSerializer

    def get_queryset(self) -> QuerySet:
        """
        Переопределен метод для фильтрации по пользователю.
        """
        return Account.objects.filter(user=self.request.user)


@extend_schema(tags=["Accounts"])
class ToggleAccountActiveStatusView(generics.UpdateAPIView):
    """
    Класс для переключения активности счета.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = AccountToggleStatusSerializer
    http_method_names = ["patch"]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user.pk)

    def get_object(self):
        """
        Переопределяем метод для получения счета пользователя.
        """
        account = super().get_object()
        if account.user != self.request.user:
            raise PermissionDenied("You do not have permission to modify this account.")
        return account

    def patch(self, request, *args, **kwargs):
        """
        Обновляет статус активности счета.
        """
        account = self.get_object()
        account.is_active = not account.is_active
        account.save()

        return Response(
            AccountToggleStatusSerializer(account).data, status=status.HTTP_200_OK
        )
