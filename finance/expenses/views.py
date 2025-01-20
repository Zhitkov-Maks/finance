from datetime import datetime as dt, UTC

from django.db.models import QuerySet, Count
from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, TokenAuthentication, BasicAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filter import IncomeFilter, get_category_expense_statistics
from .models import Expense, Category
from .serializers import ExpenseSerializer, CategorySerializerExpenses, ExpenseSerializersAdd, ExpenseSerializersPut, \
    ExpenseSerializersPatch


class ExpensePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=["Expenses"])
@extend_schema_view(
    get=extend_schema(
        description="Получить список расходов у конкретного пользователя..",
        responses={
            200: ExpenseSerializer(),
        },
    ),
    post=extend_schema(
        description="Создать новый расход.",
        request=ExpenseSerializersAdd,
        responses={
            201: ExpenseSerializer,
        },
    ),
)
class ExpenseView(generics.ListCreateAPIView):
    pagination_class = ExpensePagination
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
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        """
        Переопределяем чтобы,
         выбрать нужный сериализатор для разных методов.
        :return:
        """
        if self.request.method == 'POST':
            return ExpenseSerializersAdd
        return ExpenseSerializer

    def perform_create(self, serializer) -> None:
        """
        Переопределяем метод, чтобы при добавлении расхода минусовать сумму расхода
        с выбранного счета.
        :param serializer: Сериализатор.
        """
        # Сохранение объекта с текущим пользователем и пришедшими данными
        income = serializer.save(user=self.request.user)
        # Получаем счет куда поступил расход
        account = income.account
        # Обновляем и сохраняем баланс счета
        account.balance -= income.amount
        account.save()


@extend_schema(tags=["Expenses"])
@extend_schema_view(
    get=extend_schema(
        description="Получение подробной информации о расходе.",
        responses={
            200: ExpenseSerializer(many=True),
        },
    ),
    put=extend_schema(
        description="Обновить все данные о расходе.",
        request=ExpenseSerializersPut,
        responses={
            200: ExpenseSerializer,
        },
    ),
    patch=extend_schema(
        description="Изменить сумму расхода",
        request=ExpenseSerializersPatch,
        responses={
            200: ExpenseSerializer,
        },
    ),
    delete=extend_schema(description="Удалить расход."),
)
@extend_schema(tags=['Expenses'])
class RetrieveUpdateDeleteExpense(generics.RetrieveUpdateDestroyAPIView):
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
        account = instance.account  # Получаем счет, с которого был списан расход
        amount = instance.amount  # Сохраняем сумму расхода

        # Обновляем баланс счета, добавляя обратно сумму расхода
        account.balance += amount  # Предполагается, что у вас есть поле balance в модели Account
        account.save()
        instance.delete()


class ExpenseCategoryPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=["Expenses_category"])
@extend_schema_view(
    get=extend_schema(
        description="Получить список категорий расходов..",
        responses={
            200: CategorySerializerExpenses(),
        },
    ),
    post=extend_schema(
        description="Создать новую категорию для расходов.",
        request=ExpenseSerializersAdd,
        responses={
            201: CategorySerializerExpenses,
        },
    ),
)
class ListCategoryExpense(generics.ListCreateAPIView):
    serializer_class = CategorySerializerExpenses
    pagination_class = ExpenseCategoryPagination
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
            Category.objects
            .filter(user=self.request.user)
            .annotate(usage_count=Count('expenses'))
            .order_by('-usage_count')
        )

    def perform_create(self, serializer) -> None:
        """Связываем категорию и пользователя."""
        serializer.save(user=self.request.user)


@extend_schema(tags=["Expenses_category"])
@extend_schema_view(
    get=extend_schema(
        description="Получение подробной информации о категории.",
        responses={
            200: CategorySerializerExpenses(),
        },
    ),
    put=extend_schema(
        description="Обновить данные о категории расхода",
        request=CategorySerializerExpenses,
        responses={
            200: ExpenseSerializer,
        },
    ),
    delete=extend_schema(description="Удалить категорию расхода."),
)
class RetrieveUpdateDeleteCategoryExpense(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializerExpenses
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self) -> QuerySet:
        """
        Переопределяем метод, чтобы возвращать категории по конкретному пользователю.
        :return Queryset:
        """
        return Category.objects.filter(user=self.request.user)


class CategoryExpenseStatisticsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    @extend_schema(tags=["Expenses"])
    @extend_schema(
        parameters=[
            OpenApiParameter('year', int, description='Год для статистики', required=True),
            OpenApiParameter('month', int, description='Месяц для статистики', required=True),
        ]
    )
    def get(self, request, *args, **kwargs) -> Response:
        """
        Метод для получения статистики за выбранный месяц.
        :return: Список с категориями и суммой расхода за эту категорию.
        """
        year: int = request.query_params.get('year', dt.now(UTC).year)
        month: int = request.query_params.get('month', dt.now(UTC).month)
        if not year or not month:
            return Response({"error": "Year and month are required."}, status=400)

        statistics = get_category_expense_statistics(request.user, year, month)
        return Response(statistics)
