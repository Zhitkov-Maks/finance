from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from transfer.serializers import (
    IsNotAuthentication,
    NotFoundError,
    ValidationError,
)

from .serializers import (
    CategorySerializer,
    CategoryTransactionStatisticsSerializer,
    TransactionSerializer,
    TransactionSerializerGet,
    TransactionSerializersAdd,
    TransactionSerializersPatch,
)

TtransactionViewSchema = extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "type", str,
                description="Тип транзакции(income, expence)",
                required=True
            )],
        description="Получить список транзакций у конкретного пользователя.",
        responses={
            200: TransactionSerializer,
            401: IsNotAuthentication,
        },
    ),
    post=extend_schema(
        description="Создать новую транзакцию.",
        request=TransactionSerializersAdd,
        responses={
            201: TransactionSerializer,
            400: ValidationError,
            401: IsNotAuthentication,
        },
    ),
)


RetrieveUpdateDeleteTransactionSchema = extend_schema_view(
    get=extend_schema(
        description="Получение подробной информации о транзакции.",
        responses={
            200: TransactionSerializerGet(many=True),
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    put=extend_schema(
        description="Обновить все данные о доходе.",
        request=TransactionSerializersAdd,
        responses={
            200: TransactionSerializersAdd,
            400: ValidationError,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    patch=extend_schema(
        description="Изменить сумму транзакции",
        request=TransactionSerializersPatch,
        responses={
            200: TransactionSerializersAdd,
            400: ValidationError,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    delete=extend_schema(
        description="Удалить транзакцию.",
        responses={
            204: None,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
)


ListCategoryTransactionSchema = extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "type", str,
                description="Тип транзакции(income, expence)",
                required=True
            )],
        description="Получить список категорий.",
        responses={
            200: CategorySerializer,
            401: IsNotAuthentication,
        },
    ),
    post=extend_schema(
        parameters=[
            OpenApiParameter(
                "type", str,
                description="Тип транзакции(income, expence)",
                required=True
            )],
        description="Создать новую категорию.",
        request=CategorySerializer,
        responses={
            201: CategorySerializer,
            400: ValidationError,
            401: IsNotAuthentication,
        },
    ),
)


RetrieveUpdateDeleteCategoryTransactionSchema = extend_schema_view(
    get=extend_schema(
        description="Получение подробной информации о категории.",
        responses={
            200: CategorySerializer,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    put=extend_schema(
        description="Обновить данные о категории",
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: ValidationError,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    delete=extend_schema(
        description="Удалить категорию.",
        responses={
            204: None,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
)


transaction_statistic_schema = extend_schema_view(
    get=extend_schema(
        tags=["TransactionStatistic"],
        parameters=[
            OpenApiParameter(
                "year", int,
                description="Год для статистики",
                required=True
            ),
            OpenApiParameter(
                "month", int,
                description="Месяц для статистики",
                required=True
            ),
            OpenApiParameter(
                "type", str,
                description="тип транзакции",
                required=True
            ),
        ],
        description="Получение статистики за переданный месяц и год.",
        responses={
            200: CategoryTransactionStatisticsSerializer,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    )
)
