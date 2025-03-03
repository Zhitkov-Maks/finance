from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema
)

from accounts.serializers import AccountSerializer
from .serializers import (
    IsNotAuthentication,
    NotFoundError,
    TransferSerializer, ValidationError
)

# Схемы для просмотра, удаления и редактирования конкретного перевода.
TransferRetrieveViewSchema = extend_schema_view(
    get=extend_schema(
        description="Получить детали перевода по ID.",
        responses={
            201: AccountSerializer,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    put=extend_schema(
        description="Обновить детали перевода по ID.",
        request=TransferSerializer,
        responses={
            200: TransferSerializer,
            400: ValidationError,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
    delete=extend_schema(
        description="Удалить перевод по ID.",
        responses={
            204: None,
            400: ValidationError,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    ),
)


# Схема для создания перевода
TransferSchema = extend_schema_view(
    post=extend_schema(
        description="Метод для перевода денег между своими счетами",
        request=TransferSerializer,
        responses={
            201: TransferSerializer,
            400: ValidationError,
            401: IsNotAuthentication,
        },
    )
)


# Схема для получения списка переводов
TransferHistoryViewSchema = extend_schema_view(
    get=extend_schema(
        description="Получить историю переводов для текущего пользователя.",
        responses={
            200: TransferSerializer(many=True),
            401: IsNotAuthentication,
        },
    )
)
