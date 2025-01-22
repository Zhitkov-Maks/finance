from django.db.models import QuerySet
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

from .models import Account
from .schemas import listAccountSchema, RetrieveUpdateDeleteAccountSchema
from .serialisers import (
    AccountSerializer,
    AccountSerializerDetail
)


class AccountPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=["Accounts"])
@listAccountSchema
class ListAccounts(generics.ListCreateAPIView):
    pagination_class = AccountPagination
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self) -> QuerySet:
        """
        Переопределил метод для показа счетов только конкретного пользователя.
        :return Queryset: Список счетов пользователя.
        """
        return Account.objects.filter(user=self.request.user.pk).order_by("-balance")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


@extend_schema(tags=["Accounts"])
@RetrieveUpdateDeleteAccountSchema
class RetrieveUpdateDeleteAccount(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_serializer_class(self):
        """
        Переопределен метод для выбора сериализатора в зависимости от запроса.
        :return:
        """
        if self.request.method == "GET":
            return AccountSerializerDetail
        return AccountSerializer

    def get_queryset(self) -> QuerySet:
        return Account.objects.filter(user=self.request.user)
