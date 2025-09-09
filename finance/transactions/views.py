import decimal
from datetime import datetime as dt, UTC

from django.db.models import QuerySet, Count
from rest_framework import serializers
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
from app_user.models import CustomUser
from .filter import TransactionFilter, get_category_statistics
from .models import Transaction, Category
from .schemas import (
    TtransactionViewSchema,
    RetrieveUpdateDeleteTransactionSchema,
    ListCategoryTransactionSchema,
    RetrieveUpdateDeleteCategoryTransactionSchema,
    transaction_statistic_schema,
)
from .serializers import (
    TransactionSerializer,
    CategorySerializer,
    TransactionSerializersAdd,
    TransactionSerializerGet,
    TransactionSerializersPatch,
    StatisticsResponseSerializer,
)


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=["Transactions"])
@TtransactionViewSchema
class TransactionView(generics.ListCreateAPIView):
    """
    Класс для получения списка транзакций и создания новой транзакции.
    """
    queryset = Transaction.objects.none()
    pagination_class = Pagination
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TransactionFilter
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self) -> QuerySet:
        """
        Метод переопределен для фильтрации доходов по пользователю.
        """
        queryset = Transaction.objects.filter(user=self.request.user)
        if transaction_type := self.request.query_params.get('type'):
            queryset = queryset.filter(
                category__type_transaction=transaction_type
            )
        return queryset

    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от метода.
        """
        if self.request.method == "POST":
            return TransactionSerializersAdd
        return TransactionSerializer

    def perform_create(self, serializer) -> None:
        """
        Добавление баланса в выбранный счет.
        """
        type_transaction = self.request.query_params.get('type')
        transaction: Transaction = serializer.save(user=self.request.user)
        account: Account = transaction.account

        if type_transaction.startswith("inc"):
            account.balance += transaction.amount
        else:
            account.balance -= transaction.amount
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
        response_serializer = TransactionSerializer(serializer.instance)

        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )


@extend_schema(tags=["Transactions"])
@RetrieveUpdateDeleteTransactionSchema
class RetrieveUpdateDeleteTransaction(generics.RetrieveUpdateDestroyAPIView):
    """
    Класс для редактирования, удаления и получения детальной
    информации о транзакции.
    """
    queryset = Transaction.objects.none()
    serializer_class = TransactionSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_serializer_class(self):

        if self.request.method == "PUT":
            return TransactionSerializersAdd

        elif self.request.method == "PATCH":
            return TransactionSerializersPatch

        elif self.request.method == "GET":
            return TransactionSerializerGet

        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        """
        Метод переопределен для фильтрации по пользователю.
        :return:
        """
        return Transaction.objects.filter(user=self.request.user)

    def perform_destroy(self, instance: Transaction) -> None:
        """
        Переопределяем метод, чтобы вычесть сумму дохода из баланса счета,
        на который был доход.
        :param instance: Объект дохода.
        """
        account: Account = instance.account  # Получаем счет
        amount: decimal = instance.amount  # Сохраняем сумму дохода

        if instance.category.type_transaction == "income":
            account.balance -= amount
        else:
            account.balance += amount
        account.save()
        instance.delete()

    def perform_update(self, serializer: TransactionSerializer) -> None:
        """
        Переопределяем метод для обновления дохода и корректировки
        баланса счета.
        :param serializer: Сериализатор с новыми данными.
        """
        instance: Transaction = self.get_object()
        type_transaction: str = instance.category.type_transaction
        old_account: Account = instance.account
        new_account: Account = serializer.validated_data.get(
            "account", old_account
        )

        old_amount: decimal = instance.amount
        new_amount: decimal = serializer.validated_data.get(
            "amount", old_amount
        )

        serializer.save()

        if new_account != old_account:
            if type_transaction.startswith("exp"):
                old_account.balance += old_amount
                new_account.balance -= new_amount
            else:
                old_account.balance -= old_amount
                new_account.balance += new_amount
            Account.objects.bulk_update(
                (new_account, old_account), ["balance"]
            )
        else:
            if type_transaction.startswith("inc"):
                old_account.balance += new_amount - old_amount
            else:
                old_account.balance += old_amount - new_amount
            old_account.save()


@extend_schema(tags=["TransactionCategory"])
@ListCategoryTransactionSchema
class ListCategory(generics.ListCreateAPIView):
    """
    Класс для получения списка категорий пользователя,
    а так же создания новой категории.
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
        :return QuerySet: Список категорий транзакций.
        """
        queryset = (
            Category.objects.filter(user=self.request.user)
            .annotate(usage_count=Count("transactions"))
            .order_by("-usage_count", "name")
        )
        if transaction_type := self.request.query_params.get('type'):
            queryset = queryset.filter(type_transaction=transaction_type)
        return queryset

    def perform_create(self, serializer):
        """
        Связываем категорию и пользователя.
        Проверяем на существование.
        """
        user: CustomUser = self.request.user
        type_transaction = self.request.query_params.get('type')
        category_name: str = serializer.validated_data['name']
        existing_category = Category.objects.filter(
            user=user, name=category_name, type_transaction=type_transaction
        ).first()

        if existing_category:
            raise serializers.ValidationError(
                {"detail": "Категория с таким именем уже существует."}
            )
        else:
            serializer.save(user=user, type_transaction=type_transaction)


@extend_schema(tags=["TransactionCategory"])
@RetrieveUpdateDeleteCategoryTransactionSchema
class RetrieveUpdateDeleteCategory(generics.RetrieveUpdateDestroyAPIView):
    """
    Класс для редактирования категорий, удаления и получения
    подробной информации.
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


@transaction_statistic_schema
class CategoryTransactionStatisticsView(generics.GenericAPIView):
    """
    Класс для получения статистики по переданному году и 
    месяцу и типу транзакции.
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
        type_tr: int = request.query_params.get("type", dt.now(UTC).month)
        if not year or not month or not type_tr:
            return Response(
                {"error": "Year and month are required."},
                status=400
            )

        statistics: QuerySet = get_category_statistics(
            request.user, year, month, type_tr=type_tr
        )
        total_amount: float = sum(
            float(item['total_amount']) for item in statistics
        )

        response_data: dict[str, QuerySet | float] = {
            "statistics": statistics,
            "total_amount": total_amount,
        }
        serializer: StatisticsResponseSerializer = self.get_serializer(
            response_data
        )
        return Response(serializer.data)
