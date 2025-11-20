from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view
)

from .serializers import FormattedMonthlyAnalyticsSerializer
from transfer.serializers import (
    IsNotAuthentication,
    NotFoundError
)


transaction_analytic_schema = extend_schema_view(
    get=extend_schema(
        operation_id="get_analytic_transactions",
        tags=["Analytics"],
        parameters=[
            OpenApiParameter(
                "year", int,
                description="Год для статистики",
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
            200: FormattedMonthlyAnalyticsSerializer,
            401: IsNotAuthentication,
            404: NotFoundError,
        },
    )
)