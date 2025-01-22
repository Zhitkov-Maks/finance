# category_schemas.py
from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import (
    CategorySerializer,
    IncomeSerializer,
    IncomeSerializersAdd
)



IncomesViewSchema = extend_schema_view(
    get=extend_schema(
        description="Получить список доходов у конкретного пользователя..",
        responses={
            200: IncomeSerializer(),
        },
    ),
    post=extend_schema(
        description="Создать новый доход.",
        request=IncomeSerializersAdd,
        responses={
            201: IncomeSerializer,
        },
    ),
)


RetrieveUpdateDeleteIncomeSchema = extend_schema_view(
    get=extend_schema(
        description="Получение подробной информации о доходе.",
        responses={
            200: IncomeSerializersAdd(many=True),
        },
    ),
    put=extend_schema(
        description="Обновить все данные о доходе.",
        request=IncomeSerializersAdd,
        responses={
            200: IncomeSerializersAdd,
        },
    ),
    patch=extend_schema(
        description="Изменить сумму дохода",
        request=IncomeSerializersAdd,
        responses={
            200: IncomeSerializersAdd,
        },
    ),
    delete=extend_schema(description="Удалить доход."),
)


ListCategoryIncomeSchema = extend_schema_view(
    get=extend_schema(
        description="Получить список категорий доходов..",
        responses={
            200: CategorySerializer(),
        },
    ),
    post=extend_schema(
        description="Создать новую категорию дохода.",
        request=CategorySerializer,
        responses={
            201: CategorySerializer,
        },
    ),
)


RetrieveUpdateDeleteCategoryIncomeSchema = extend_schema_view(
    get=extend_schema(
        description="Получение подробной информации о категории.",
        responses={
            200: CategorySerializer(),
        },
    ),
    put=extend_schema(
        description="Обновить данные о категории дохода",
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
        },
    ),
    delete=extend_schema(description="Удалить категорию дохода."),
)
