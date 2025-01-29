from drf_spectacular.utils import extend_schema, extend_schema_view

from accounts.serializers.serializers_transfer import (
    ValidationError,
    IsNotAuthentication,
    NotFoundError,
)
from .serializers import CategorySerializer, IncomeSerializer, IncomeSerializersAdd

IncomesViewSchema = extend_schema_view(
    get=extend_schema(
        description="Получить список доходов у конкретного пользователя..",
        responses={
            200: IncomeSerializer,
            401: IsNotAuthentication,
        },
    ),
    post=extend_schema(
        description="Создать новый доход.",
        request=IncomeSerializersAdd,
        responses={
            201: IncomeSerializer,
            400: ValidationError,
            401: IsNotAuthentication,
        },
    ),
)


RetrieveUpdateDeleteIncomeSchema = extend_schema_view(
    get=extend_schema(
        description="Получение подробной информации о доходе.",
        responses={
            200: IncomeSerializersAdd(many=True),
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    put=extend_schema(
        description="Обновить все данные о доходе.",
        request=IncomeSerializersAdd,
        responses={
            200: IncomeSerializersAdd,
            400: ValidationError,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    patch=extend_schema(
        description="Изменить сумму дохода",
        request=IncomeSerializersAdd,
        responses={
            200: IncomeSerializersAdd,
            400: ValidationError,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    delete=extend_schema(
        description="Удалить доход.",
        responses={
            204: None,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
)


ListCategoryIncomeSchema = extend_schema_view(
    get=extend_schema(
        description="Получить список категорий доходов..",
        responses={
            200: CategorySerializer,
            401: IsNotAuthentication,
        },
    ),
    post=extend_schema(
        description="Создать новую категорию дохода.",
        request=CategorySerializer,
        responses={
            201: CategorySerializer,
            400: ValidationError,
            401: IsNotAuthentication,
        },
    ),
)


RetrieveUpdateDeleteCategoryIncomeSchema = extend_schema_view(
    get=extend_schema(
        description="Получение подробной информации о категории.",
        responses={
            200: CategorySerializer,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    put=extend_schema(
        description="Обновить данные о категории дохода",
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: ValidationError,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    delete=extend_schema(
        description="Удалить категорию дохода.",
        responses={
            204: None,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
)
