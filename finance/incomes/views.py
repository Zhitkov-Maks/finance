from django.db.models import QuerySet
from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .filter import IncomeFilter
from .models import Income, Category
from .serializers import IncomeSerializer, CategorySerializer, IncomeSerializersAdd


class IncomePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=['Incomes'])
class IncomeView(generics.ListCreateAPIView):
    pagination_class = IncomePagination
    serializer_class = IncomeSerializersAdd
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IncomeFilter
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self) -> QuerySet:
        return Income.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return IncomeSerializersAdd
        return IncomeSerializer

    def perform_create(self, serializer) -> None:
        # Сохранение объекта с текущим пользователем и пришедшими данными
        income = serializer.save(user=self.request.user)
        # Получаем счет куда поступил доход
        account = income.account
        # Обновляем и сохраняем баланс счета
        account.balance += income.amount  # Добавьте сумму дохода к балансу
        account.save()


@extend_schema(tags=['Incomes'])
class RetrieveUpdateDeleteIncome(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IncomeSerializersAdd
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)


class CategoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=['Incomes'])
class ListCategory(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=['Incomes'])
class RetrieveUpdateDeleteCategory(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
