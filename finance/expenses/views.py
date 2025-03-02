import decimal
from datetime import datetime as dt, UTC

from django.db.models import QuerySet, Count
from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
    BasicAuthentication,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Account
from .filter import ExpenseFilter, get_category_expense_statistics
from .models import Expense, Category
from .serializers import (
    ExpenseSerializer,
    CategorySerializerExpenses,
    ExpenseSerializersAdd,
    ExpenseSerializersPatch,
    ExpenseSerializersPut,
    StatisticsResponseSerializer,
)
from .views_schemas import (
    RetrieveUpdateDeleteCategoryExpenseSchema,
    ExpenseViewSchema,
    RetrieveUpdateDeleteExpenseSchema,
    ListCategoryExpenseSchema, expense_statistic_schema,
)


class Pagination(PageNumberPagination):
    """
    Класс для реализации пагинации.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=["Expenses"])
@ExpenseViewSchema
class ExpenseView(generics.ListCreateAPIView):
    """
    Класс для добавления расхода и для показа списка расходов.
    """

    pagination_class = Pagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ExpenseFilter
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self) -> QuerySet:
        """
        Переопределяем метод для фильтрации по пользователю.
        :return: Список расходов.
        """
        return Expense.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        """
        Добавляем request в сериализатор.
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_serializer_class(self):
        """
        Переопределяем чтобы,
        выбрать нужный сериализатор для разных методов.
        :return:
        """
        if self.request.method == "POST":
            return ExpenseSerializersAdd
        return ExpenseSerializer

    def perform_create(self, serializer) -> None:
        """
        Переопределяем метод, чтобы при добавлении расхода минусовать
        сумму расхода с выбранного счета.
        :param serializer: Сериализатор.
        """
        expense: Expense = serializer.save(user=self.request.user)
        account: Account = expense.account
        account.balance -= expense.amount
        account.save()

    def create(self, request, *args, **kwargs):
        """
        Переопределение метода создания для возврата сериализованного
        объекта с использованием другого сериализатора.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        # Используем другой сериализатор для возврата созданного объекта
        response_serializer = ExpenseSerializer(serializer.instance)

        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )


@extend_schema(tags=["Expenses"])
@RetrieveUpdateDeleteExpenseSchema
class RetrieveUpdateDeleteExpense(generics.RetrieveUpdateDestroyAPIView):
    """
    Класс для редактирования, удаления и получения
    детальной информации о расходе.
    """

    serializer_class = ExpenseSerializersAdd
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self) -> QuerySet:
        """
        Переопределяем метод, для получения списка расходов
        только по конкретному пользователю.
        :return:
        """
        return Expense.objects.filter(user=self.request.user)

    def get_serializer_class(self):

        if self.request.method == "PUT":
            return ExpenseSerializersPut

        elif self.request.method == "PATCH":
            return ExpenseSerializersPatch

        elif self.request.method == "GET":
            return ExpenseSerializer

        return super().get_serializer_class()

    def perform_destroy(self, instance: Expense) -> None:
        """
        Переопределяем метод, чтобы вернуть сумму расхода на баланс счета,
        с которого было списание.
        :param instance: Объект расхода.
        """
        account: Account = (
            instance.account
        )
        amount: decimal = instance.amount

        account.balance += amount
        account.save()
        instance.delete()

    def perform_update(self, serializer: ExpenseSerializer) -> None:
        """
        Переопределяем метод для обновления дохода и корректировки
        баланса счета.
        :param serializer: Сериализатор с новыми данными.
        """
        instance: Expense = self.get_object()

        old_account: Account = instance.account
        new_account: Account = serializer.validated_data.get(
            "account", old_account
        )

        # Получаем старую и новую сумму
        old_amount: decimal = instance.amount
        new_amount: decimal = serializer.validated_data.get(
            "amount", old_amount
        )

        serializer.save()

        if new_account != old_account:
            old_account.balance += old_amount
            old_account.save()

            new_account.balance -= new_amount
            new_account.save()
        else:
            old_account.balance += old_amount - new_amount
            old_account.save()

    def perform_create(self, serializer: ExpenseSerializer) -> None:
        """
        Переопределяем метод для создания нового расхода и
        корректировки баланса счета.
        :param serializer: Сериализатор с новыми данными.
        """
        expense: Expense = serializer.save(user=self.request.user)

        account: Account = expense.account
        amount: decimal = expense.amount
        account.balance -= amount
        account.save()



@extend_schema(tags=["Expenses_category"])
@ListCategoryExpenseSchema
class ListCategoryExpense(generics.ListCreateAPIView):
    """
    Класс для получения списка категорий у пользователя, а так же создание
    новой категории.
    """

    serializer_class = CategorySerializerExpenses
    pagination_class = Pagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self) -> QuerySet:
        """
        Переопределили метод, чтобы возвращать категории по частоте
        использования. Чтобы приходили первыми наиболее часто используемые.
        :return QuerySet:  Возвращает список категорий расходов.
        """
        return (
            Category.objects.filter(user=self.request.user)
            .annotate(usage_count=Count("expenses"))
            .order_by("-usage_count", "name")
        )

    def perform_create(self, serializer) -> None:
        """Связываем категорию и пользователя."""
        serializer.save(user=self.request.user)


@extend_schema(tags=["Expenses_category"])
@RetrieveUpdateDeleteCategoryExpenseSchema
class RetrieveUpdateDeleteCategoryExpense(generics.RetrieveUpdateDestroyAPIView):
    """
    Класс для редактирования, удаления и получения детальной информации
    о категории.
    """

    serializer_class = CategorySerializerExpenses
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names: list = ["get", "put", "delete"]

    def get_queryset(self) -> QuerySet:
        """
        Переопределяем метод, чтобы возвращать категории по конкретному
        пользователю.
        :return Queryset:
        """
        return Category.objects.filter(user=self.request.user)


@expense_statistic_schema
class CategoryExpenseStatisticsView(generics.GenericAPIView):
    """
    Класс для получения статистики по переданному году и месяцу.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    serializer_class = StatisticsResponseSerializer

    def get(self, request, *args, **kwargs) -> Response:
        """
        Метод для получения статистики за выбранный месяц.
        :return: Список с категориями и суммой расхода за эту категорию.
        """
        year: int = request.query_params.get("year", dt.now(UTC).year)
        month: int = request.query_params.get("month", dt.now(UTC).month)
        if not year or not month:
            return Response(
                {"error": "Year and month are required."},
                status=400
            )

        statistics = get_category_expense_statistics(request.user, year, month)
        total_amount = sum(float(item['total_amount']) for item in statistics)

        response_data = {
            "statistics": statistics,
            "total_amount": total_amount,
        }
        serializer = self.get_serializer(response_data)
        return Response(serializer.data)
