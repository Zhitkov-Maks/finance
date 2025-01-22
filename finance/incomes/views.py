import decimal

from django.db.models import QuerySet, Count
from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
    BasicAuthentication,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from accounts.models import Account
from .filter import IncomeFilter
from .models import Income, Category
from .schemas import (
    IncomesViewSchema,
    RetrieveUpdateDeleteIncomeSchema,
    ListCategoryIncomeSchema,
    RetrieveUpdateDeleteCategoryIncomeSchema,
)
from .serializers import IncomeSerializer, CategorySerializer, IncomeSerializersAdd


class IncomePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=["Incomes"])
@IncomesViewSchema
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
        if self.request.method == "POST":
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


@extend_schema(tags=["Incomes"])
@RetrieveUpdateDeleteIncomeSchema
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

    def perform_destroy(self, instance: Income) -> None:
        """
        Переопределяем метод, чтобы вычесть сумму дохода из баланса счета,
        на который был доход.
        :param instance: Объект дохода.
        """
        account: Account = instance.account  # Получаем счет
        amount = instance.amount  # Сохраняем сумму дохода

        # Обновляем баланс счета
        account.balance -= amount
        account.save()
        instance.delete()

    def perform_update(self, serializer: IncomeSerializer) -> None:
        """
        Переопределяем метод для обновления дохода и корректировки баланса счета.
        :param serializer: Сериализатор с новыми данными.
        """
        instance: Income = self.get_object()
        old_amount: decimal = instance.amount
        new_amount: decimal = serializer.validated_data.get("amount", old_amount)
        serializer.save()

        # Получаем счет, связанный с доходом
        account: Account = instance.account
        # Корректируем баланс: вычитаем старую сумму и добавляем новую
        account.balance -= new_amount - old_amount
        account.save()


class CategoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=["Incomes_category"])
@ListCategoryIncomeSchema
class ListCategory(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self) -> QuerySet:
        """
        Переопределен метод для возврата доходов только
        конкретного пользователя и сортировке сетов по частоте использования.
        :return QuerySet: Список категорий доходов.
        """
        return (
            Category.objects.filter(user=self.request.user)
            .annotate(usage_count=Count("incomes"))
            .order_by("-usage_count")
        )

    def perform_create(self, serializer) -> None:
        """Связываем категорию и пользователя."""
        serializer.save(user=self.request.user)


@extend_schema(tags=["Incomes_category"])
@RetrieveUpdateDeleteCategoryIncomeSchema
class RetrieveUpdateDeleteCategory(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self) -> QuerySet:
        """
        Переопределил, чтобы пользователь мог получить доступ только к своим
        собственным категориям, а не к категориям других пользователей.
        """
        return Category.objects.filter(user=self.request.user)
