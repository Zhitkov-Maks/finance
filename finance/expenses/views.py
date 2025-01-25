import decimal
from datetime import datetime as dt, UTC

from django.db.models import QuerySet, Count
from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import generics
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
    BasicAuthentication,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Account
from accounts.serializers.serializers_transfer import NotFoundError, IsNotAuthentication
from incomes.serializers import CategoryIncomeStatisticsSerializer
from .filter import IncomeFilter, get_category_expense_statistics
from .models import Expense, Category
from .serializers import (
    ExpenseSerializer,
    CategorySerializerExpenses,
    ExpenseSerializersAdd,
    CategoryExpenseStatisticsSerializer,
)
from .views_schemas import (
    RetrieveUpdateDeleteCategoryExpenseSchema,
    ExpenseViewSchema,
    RetrieveUpdateDeleteExpenseSchema,
    ListCategoryExpenseSchema,
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
    serializer_class = ExpenseSerializersAdd
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IncomeFilter
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
        Переопределяем метод, чтобы при добавлении расхода минусовать сумму расхода
        с выбранного счета.
        :param serializer: Сериализатор.
        """
        expense: Expense = serializer.save(user=self.request.user)
        account: Account = expense.account
        account.balance -= expense.amount
        account.save()


@extend_schema(tags=["Expenses"])
@RetrieveUpdateDeleteExpenseSchema
class RetrieveUpdateDeleteExpense(generics.RetrieveUpdateDestroyAPIView):
    """
    Класс для редактирования, удаления и получения детальной информации о расходе.
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

    def perform_destroy(self, instance: Expense) -> None:
        """
        Переопределяем метод, чтобы вернуть сумму расхода на баланс счета,
        с которого было списание.
        :param instance: Объект расхода.
        """
        account: Account = (
            instance.account
        )  # Получаем счет, с которого был списан расход
        amount: decimal = instance.amount  # Сохраняем сумму расхода

        # Обновляем баланс счета, добавляя обратно сумму расхода
        account.balance += amount
        account.save()
        instance.delete()

    def perform_update(self, serializer) -> None:
        """
        Переопределяем метод для обновления расхода и корректировки баланса счета.
        :param serializer: Сериализатор с новыми данными.
        """
        # Получаем экземпляр расхода перед обновлением
        instance: Expense = self.get_object()

        # Сохраняем старую сумму расхода
        old_amount: decimal = instance.amount

        # Получаем новую сумму из сериализатора
        new_amount: decimal = serializer.validated_data.get("amount", old_amount)

        # Обновляем объект с новыми данными
        serializer.save()

        # Получаем счет, связанный с расходом
        account: Account = instance.account

        # Корректируем баланс: вычитаем старую сумму и добавляем новую
        account.balance += new_amount - old_amount
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
        Переопределили метод, чтобы возвращать категории по частоте использования.
        Чтобы приходили первыми наиболее часто используемые.
        :return QuerySet:  Возвращает список категорий расходов.
        """
        return (
            Category.objects.filter(user=self.request.user)
            .annotate(usage_count=Count("expenses"))
            .order_by("-usage_count")
        )

    def perform_create(self, serializer) -> None:
        """Связываем категорию и пользователя."""
        serializer.save(user=self.request.user)


@extend_schema(tags=["Expenses_category"])
@RetrieveUpdateDeleteCategoryExpenseSchema
class RetrieveUpdateDeleteCategoryExpense(generics.RetrieveUpdateDestroyAPIView):
    """
    Класс для редактирования, удаления и получения детальной информации о категории.
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
        Переопределяем метод, чтобы возвращать категории по конкретному пользователю.
        :return Queryset:
        """
        return Category.objects.filter(user=self.request.user)


@extend_schema_view(
    get=extend_schema(
        tags=["Expenses"],
        parameters=[
            OpenApiParameter(
                "year", int, description="Год для статистики", required=True
            ),
            OpenApiParameter(
                "month", int, description="Месяц для статистики", required=True
            ),
        ],
        description="Получение статистики расходов за переданный месяц и год.",
        responses={
            200: CategoryIncomeStatisticsSerializer,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    )
)
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
    serializer_class = CategoryExpenseStatisticsSerializer

    def get(self, request, *args, **kwargs) -> Response:
        """
        Метод для получения статистики за выбранный месяц.
        :return: Список с категориями и суммой расхода за эту категорию.
        """
        year: int = request.query_params.get("year", dt.now(UTC).year)
        month: int = request.query_params.get("month", dt.now(UTC).month)
        if not year or not month:
            return Response({"error": "Year and month are required."}, status=400)

        statistics = get_category_expense_statistics(request.user, year, month)
        serializer = self.get_serializer(statistics, many=True)
        return Response(serializer.data)
