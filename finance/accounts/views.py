from drf_spectacular.utils import extend_schema, extend_schema_view
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
from .serialisers import (
    AccountSerializer,
    AccountSerializerDetail,
    AccountPutSerializer,
    AccountPatchSerializer,
)


class AccountPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=["Accounts"])
@extend_schema_view(
    get=extend_schema(
        description="Получить список всех счетов текущего пользователя. "
        "Каждый аккаунт связан с пользователем и содержит "
        "информацию о балансе.",
        responses={
            200: AccountSerializer(),
        },
    ),
    post=extend_schema(
        description="Создать новый счет для текущего пользователя. "
        "Укажите название счета и начальный баланс.",
        request=AccountSerializer,
        responses={
            201: AccountSerializer,
        },
    ),
)
class ListAccounts(generics.ListCreateAPIView):
    pagination_class = AccountPagination
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self):
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
@extend_schema_view(
    get=extend_schema(
        description="Получить детальную информацию о счете. В счет добавляется информация о "
        "последних доходах и расходах за последние 30 дней.",
        responses={
            200: AccountSerializerDetail(many=True),
        },
    ),
    put=extend_schema(
        description="Обновить все данные о счете(название и баланс)",
        request=AccountPutSerializer,
        responses={
            200: AccountSerializer,
        },
    ),
    patch=extend_schema(
        description="Изменить баланс счета.",
        request=AccountPatchSerializer,
        responses={
            200: AccountSerializer,
        },
    ),
    delete=extend_schema(description="Удалить счет."),
)
class RetrieveUpdateDeleteAccount(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AccountSerializerDetail
        return AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)
