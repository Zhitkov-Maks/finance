from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter
)

from .serializers import (
    SuccessSerializer,
    DebtListSerializer,
    DebtDetailSerializer
)
from transfer.serializers import IsNotAuthentication, NotFoundError


DebtListSchema = extend_schema_view(
    get=extend_schema(
        operation_id="get_all_debts",
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
        operation_id="get_debt_by_id",
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
        operation_id="remove_debt",
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
        operation_id="create_debt",
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
        operation_id="create_account_debt",
        tags=["Debt"],
        description="Создание счетов: взять в долг, дать в долг.",
        responses={
            201: SuccessSerializer,
        }
    )
)
