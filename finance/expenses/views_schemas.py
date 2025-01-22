# category_schemas.py
from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import (
    CategorySerializerExpenses,
    ExpenseSerializer,
    ExpenseSerializersAdd, ExpenseSerializersPatch, ExpenseSerializersPut,
)



ExpenseViewSchema = extend_schema_view(
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


RetrieveUpdateDeleteExpenseSchema = extend_schema_view(
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


ListCategoryExpenseSchema = extend_schema_view(
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


RetrieveUpdateDeleteCategoryExpenseSchema = extend_schema_view(
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
