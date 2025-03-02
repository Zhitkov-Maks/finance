from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter
)
from accounts.serializers.serializers_account import (
    AccountSerializer,
    AccountSerializerDetail,
    AccountPutSerializer,
    AccountPatchSerializer,
    AccountListResponseSerializer,
)
from accounts.serializers.serializers_debt import (
    DebtDetailSerializer,
    DebtListSerializer,
    SuccessSerializer
)
from accounts.serializers.serializers_transfer import (
    TransferSerializer,
    IsNotAuthentication,
    ValidationError,
    NotFoundError,
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
            200: AccountSerializerDetail(many=True),
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


DebtListSchema = extend_schema_view(
    get=extend_schema(
        tags=["Debt"],
        parameters=[
            OpenApiParameter(
                "type", str, description="debt или lend", required=True
            ),
        ],
        description="Получение списка ваших долгов или ваших должников.",
        responses={
            200: DebtListSerializer,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    )
)


DebtDetailSchema = extend_schema_view(
    get=extend_schema(
        tags=["Debt"],
        description="Получение информации о конкретном долге.",
        responses={
            200: DebtDetailSerializer,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    )
)


DebtRepaySchema = extend_schema_view(
    post=extend_schema(
        tags=["Debt"],
        description="Работа с погашением долгов. В полу type должно быть "
                    "указано либо debt либо lend.",
        responses={
            201: SuccessSerializer,
            401: IsNotAuthentication,
            404: NotFoundError,
        }
    )
)


DebtCreateSchema = extend_schema_view(
    post=extend_schema(
        tags=["Debt"],
        description="Работа с добавлением долга.",
        responses={
            201: SuccessSerializer,
            401: IsNotAuthentication,
            404: NotFoundError,
        }
    )
)

DebtCreateAccountsSchema = extend_schema_view(
    post=extend_schema(
        tags=["Debt"],
        description="Создание счетов: взять в долг, дать в долг.",
        responses={
            201: SuccessSerializer,
        }
    )
)
