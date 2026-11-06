import logging
from datetime import UTC
from datetime import datetime as dt
from decimal import Decimal

from accounts.cache import invalidate_balance_history_cache
from accounts.models import Account
from accounts.services import maybe_start_grace_period
from app_user.models import CustomUser
from budgets.models import Budget
from django.db import IntegrityError
from django.db import transaction as db_transaction
from django.db.models import Count, F, Q, QuerySet
from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, serializers, status
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filter import TransactionFilter, get_category_statistics
from .models import Category, Transaction
from .schemas import (
    ListCategoryTransactionSchema,
    RetrieveUpdateDeleteCategoryTransactionSchema,
    RetrieveUpdateDeleteTransactionSchema,
    TtransactionViewSchema,
    transaction_statistic_schema,
)
from .serializers import (
    CategoryCreateSerializer,
    CategoryIDSerializers,
    CategorySerializer,
    StatisticsResponseSerializer,
    TransactionSerializer,
    TransactionSerializerGet,
    TransactionSerializersAdd,
    TransactionSerializersPatch,
)

logger = logging.getLogger(__name__)


def _schedule_cache_invalidation(user_id: int) -> None:
    """
    Инвалидация кэша истории баланса только после коммита транзакции.
    При откате — кэш не трогается, читатели увидят консистентное состояние.
    """
    db_transaction.on_commit(lambda: invalidate_balance_history_cache(user_id))


def _apply_transaction_to_balance(
    transaction: Transaction, old_balance: Decimal = None
) -> None:
    """Применяет транзакцию к балансу счёта."""
    is_income = transaction.type_transaction == "income"
    delta = transaction.amount if is_income else -transaction.amount

    Account.objects.filter(pk=transaction.account_id).update(
        balance=F("balance") + delta
    )
    account = Account.objects.get(pk=transaction.account_id)

    if account.account_type == Account.TYPE_CREDIT and account.balance < 0:
        maybe_start_grace_period(
            account, old_balance=old_balance, force_date=transaction.create_at.date()
        )


def _revert_transaction_from_balance(transaction: Transaction) -> None:
    """Откатывает транзакцию."""
    is_income = transaction.type_transaction == "income"
    delta = -transaction.amount if is_income else transaction.amount

    Account.objects.filter(pk=transaction.account_id).update(
        balance=F("balance") + delta
    )


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


@extend_schema(tags=["Transactions"])
@TtransactionViewSchema
class TransactionView(generics.ListCreateAPIView):
    """
    Список транзакций пользователя и создание новой.
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
        queryset = Transaction.objects.filter(user=self.request.user).select_related(
            "category", "account"
        )
        if transaction_type := self.request.query_params.get("type"):
            queryset = queryset.filter(type_transaction=transaction_type)
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TransactionSerializersAdd
        return TransactionSerializer

    def perform_create(self, serializer) -> None:
        with db_transaction.atomic():
            transaction: Transaction = serializer.save(user=self.request.user)
            old_balance = transaction.account.balance
            _apply_transaction_to_balance(transaction, old_balance=old_balance)
            _schedule_cache_invalidation(self.request.user.pk)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_serializer = TransactionSerializer(serializer.instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Transactions"])
@RetrieveUpdateDeleteTransactionSchema
class RetrieveUpdateDeleteTransaction(generics.RetrieveUpdateDestroyAPIView):
    """
    Редактирование, удаление и просмотр конкретной транзакции.
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
        if self.request.method == "PATCH":
            return TransactionSerializersPatch
        if self.request.method == "GET":
            return TransactionSerializerGet
        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        return Transaction.objects.filter(user=self.request.user).select_related(
            "category", "account"
        )

    def perform_destroy(self, instance: Transaction) -> None:
        """
        Удаляет транзакцию и атомарно откатывает её с баланса.
        """
        with db_transaction.atomic():
            _revert_transaction_from_balance(instance)
            instance.delete()
            _schedule_cache_invalidation(self.request.user.pk)

    def perform_update(self, serializer: TransactionSerializer) -> None:
        """
        Обновляет транзакцию через «откатить старое → применить новое».
        """
        old_instance: Transaction = serializer.instance

        with db_transaction.atomic():
            # 1. Откатываем старые значения
            _revert_transaction_from_balance(old_instance)

            # 2. Сохраняем новые значения
            updated: Transaction = serializer.save()

            # 3. Читаем АКТУАЛЬНЫЙ баланс из БД (после отката старой транзакции)
            # для того счёта, КУДА применяем новую транзакцию
            current_balance = Account.objects.get(pk=updated.account_id).balance

            # 4. Применяем новое (строго ОДИН раз)
            _apply_transaction_to_balance(updated, old_balance=current_balance)

            _schedule_cache_invalidation(self.request.user.pk)


@extend_schema(tags=["TransactionCategory"])
@ListCategoryTransactionSchema
class ListCategory(generics.ListCreateAPIView):
    """
    Список категорий пользователя и создание новой.
    """

    serializer_class = CategorySerializer
    pagination_class = Pagination
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CategoryCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        parent = self.request.query_params.get("parent")
        isnull_parent = parent == "true"

        queryset = (
            Category.objects.filter(user=self.request.user)
            .annotate(usage_count=Count("transactions"))
            .prefetch_related("children")
        )
        if isnull_parent:
            queryset = queryset.filter(parent__isnull=True)

        if transaction_type := self.request.query_params.get("type"):
            queryset = queryset.filter(type_transaction=transaction_type)

        return queryset.order_by("-usage_count", "name")

    def perform_create(self, serializer):
        user: CustomUser = self.request.user

        type_transaction = self.request.query_params.get("type")
        if not type_transaction:
            raise serializers.ValidationError(
                {"type": "Параметр 'type' обязателен (income или expense)."}
            )
        if type_transaction not in ("income", "expense"):
            raise serializers.ValidationError(
                {"type": "Допустимые значения: income, expense."}
            )

        category_name: str = serializer.validated_data["name"]
        parent = serializer.validated_data.get("parent", None)

        if Category.objects.filter(
            user=user,
            name=category_name,
            type_transaction=type_transaction,
            parent=parent,
        ).exists():
            raise serializers.ValidationError(
                {"detail": "Категория с таким именем уже существует."}
            )

        try:
            serializer.save(
                user=user, type_transaction=type_transaction, parent=parent
            )
        except IntegrityError:
            raise serializers.ValidationError(
                {"detail": "Категория с таким именем уже существует."}
            )


@extend_schema(tags=["TransactionCategory"])
@RetrieveUpdateDeleteCategoryTransactionSchema
class RetrieveUpdateDeleteCategory(generics.RetrieveUpdateDestroyAPIView):
    """
    Редактирование, удаление и просмотр категории.
    """

    serializer_class = CategoryIDSerializers
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["get", "put", "delete"]

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return CategoryCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        return Category.objects.filter(user=self.request.user)

    def perform_destroy(self, instance: Category) -> None:
        has_budgets = Budget.objects.filter(
            Q(category=instance) | Q(category__parent=instance)
        ).exists()
        if has_budgets:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Нельзя удалить категорию: к ней (или к её подкатегориям) "
                        "привязаны бюджеты. Сначала удалите или измените бюджеты."
                    )
                }
            )

        instance.delete()


@transaction_statistic_schema
class CategoryTransactionStatisticsView(generics.GenericAPIView):
    """
    Статистика по категориям за выбранный месяц и тип транзакции.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    serializer_class = StatisticsResponseSerializer

    def get(self, request, *args, **kwargs) -> Response:
        try:
            year = int(request.query_params.get("year", dt.now(UTC).year))
            month = int(request.query_params.get("month", dt.now(UTC).month))
        except (TypeError, ValueError):
            return Response(
                {"error": "Параметры year и month должны быть целыми числами."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not (1 <= month <= 12):
            return Response(
                {"error": "month должен быть от 1 до 12."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        type_tr = request.query_params.get("type")
        if not type_tr:
            return Response(
                {"error": "Параметр 'type' обязателен (income или expense)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if type_tr not in ("income", "expense"):
            return Response(
                {"error": "type должен быть income или expense."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        statistics: QuerySet = get_category_statistics(
            request.user, year, month, type_tr=type_tr
        )
        total_amount: float = sum(float(item["total"]) for item in statistics)

        response_data = {
            "statistics": statistics,
            "total_amount": total_amount,
        }
        serializer = self.get_serializer(response_data)
        return Response(serializer.data)
