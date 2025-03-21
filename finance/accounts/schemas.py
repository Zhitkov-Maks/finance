from drf_spectacular.utils import extend_schema_view, extend_schema
from accounts.serializers import (
    AccountSerializer,
    AccountPutSerializer,
    AccountPatchSerializer,
    AccountListResponseSerializer,
)
from transfer.serializers import (
    IsNotAuthentication,
    ValidationError, NotFoundError
)


# Assuming AccountSerializer is defined correctly elsewhere
listAccountSchema = extend_schema_view(
    get=extend_schema(
        description="Получить список всех счетов текущего пользователя. "
                    "Каждый аккаунт связан с пользователем и содержит "
                    "информацию о балансе.",
        responses={
            200: AccountListResponseSerializer,
            401: IsNotAuthentication,
        },
    ),
    post=extend_schema(
        description="Создать новый счет для текущего пользователя. "
                    "Укажите название счета и начальный баланс.",
        request=AccountPutSerializer,
        responses={
            201: AccountSerializer,
            400: ValidationError,
            401: IsNotAuthentication,
        },
    ),
)


# Схемы для просмотра, удаления и редактирования конкретного счета.
RetrieveUpdateDeleteAccountSchema = extend_schema_view(
    get=extend_schema(
        description="Получить детальную информацию о счете. В счет добавляется "
                    "информация о последних доходах и расходах за "
                    "последние 30 дней.",
        responses={
            200: AccountSerializer(many=True),
            404: NotFoundError,
            401: IsNotAuthentication,
        },
    ),
    put=extend_schema(
        description="Обновить все данные о счете(название и баланс)",
        request=AccountPutSerializer,
        responses={
            200: AccountSerializer,
            400: ValidationError,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    patch=extend_schema(
        description="Изменить баланс счета.",
        request=AccountPatchSerializer,
        responses={
            200: AccountSerializer,
            400: ValidationError,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    delete=extend_schema(
        description="Удалить счет по ID.",
        responses={
            204: None,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
)
