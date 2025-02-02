import decimal
from datetime import datetime as dt, UTC

from django.db.models import QuerySet, Count
from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
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
from accounts.serializers.serializers_transfer import NotFoundError, IsNotAuthentication
from .filter import IncomeFilter, get_category_income_statistics
from .models import Income, Category
from .schemas import (
    IncomesViewSchema,
    RetrieveUpdateDeleteIncomeSchema,
    ListCategoryIncomeSchema,
    RetrieveUpdateDeleteCategoryIncomeSchema,
)
from .serializers import (
    IncomeSerializer,
    CategorySerializer,
    IncomeSerializersAdd,
    CategoryIncomeStatisticsSerializer, IncomeSerializerGet, IncomeSerializersPatch,
)


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=["Incomes"])
@IncomesViewSchema
class IncomeView(generics.ListCreateAPIView):
    """
    Класс для получения списка доходов и создания нового дохода.
    """

    pagination_class = Pagination
    serializer_class = IncomeSerializer
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
        Метод переопределен для фильтрации доходов по пользователю.
        """
        return Income.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от метода.
        """
        if self.request.method == "POST":
            return IncomeSerializersAdd
        return IncomeSerializer

    def perform_create(self, serializer) -> None:
        """
        Добавление баланса в выбранный счет.
        """
        income: Income = serializer.save(user=self.request.user)
        account: Account = income.account
        account.balance += income.amount
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
        response_serializer = IncomeSerializer(serializer.instance)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Incomes"])
@RetrieveUpdateDeleteIncomeSchema
class RetrieveUpdateDeleteIncome(generics.RetrieveUpdateDestroyAPIView):
    """
    Класс для редактирования, удаления и получения детальной информации о доходе.
    """

    serializer_class = IncomeSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_serializer_class(self):

        if self.request.method == "PUT":
            return IncomeSerializersAdd

        elif self.request.method == "PATCH":
            return IncomeSerializersPatch

        elif self.request.method == "GET":
            return IncomeSerializerGet

        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        """
        Метод переопределен для фильтрации по пользователю.
        :return:
        """
        return Income.objects.filter(user=self.request.user)

    def perform_destroy(self, instance: Income) -> None:
        """
        Переопределяем метод, чтобы вычесть сумму дохода из баланса счета,
        на который был доход.
        :param instance: Объект дохода.
        """
        account: Account = instance.account  # Получаем счет
        amount: decimal = instance.amount  # Сохраняем сумму дохода

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

        account: Account = instance.account
        account.balance -= new_amount - old_amount
        account.save()


@extend_schema(tags=["Incomes_category"])
@ListCategoryIncomeSchema
class ListCategory(generics.ListCreateAPIView):
    """
    Класс для получения списка категорий пользователя, а так же создания новой категории.
    """

    serializer_class = CategorySerializer
    pagination_class = Pagination
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
    """
    Класс для редактирования категорий, удаления и получения подробной информации.
    """

    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self) -> QuerySet:
        """
        Переопределил, чтобы пользователь мог получить доступ только к своим
        собственным категориям, а не к категориям других пользователей.
        """
        return Category.objects.filter(user=self.request.user)


@extend_schema_view(
    get=extend_schema(
        tags=["Incomes"],
        parameters=[
            OpenApiParameter(
                "year", int, description="Год для статистики", required=True
            ),
            OpenApiParameter(
                "month", int, description="Месяц для статистики", required=True
            ),
        ],
        description="Получение статистики доходов за переданный месяц и год.",
        responses={
            200: CategoryIncomeStatisticsSerializer,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    )
)
class CategoryIncomeStatisticsView(generics.GenericAPIView):
    """
    Класс для получения статистики доходов по переданному году и месяцу.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    serializer_class = CategoryIncomeStatisticsSerializer

    def get(self, request, *args, **kwargs) -> Response:
        """
        Метод для получения статистики за выбранный месяц.
        :return: Список с категориями и суммой расхода за эту категорию.
        """
        year: int = request.query_params.get("year", dt.now(UTC).year)
        month: int = request.query_params.get("month", dt.now(UTC).month)
        if not year or not month:
            return Response({"error": "Year and month are required."}, status=400)

        statistics = get_category_income_statistics(request.user, year, month)
        serializer = self.get_serializer(statistics, many=True)
        return Response(serializer.data)
