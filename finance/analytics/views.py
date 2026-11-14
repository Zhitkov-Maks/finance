from datetime import UTC
from datetime import datetime as dt

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filter import DailyAnalyticsService, MonthlyAnalyticsService
from .forecast import ForecastService
from .schemas import transaction_analytic_schema
from .serializers import FormattedMonthlyAnalyticsSerializer


@extend_schema(tags=["Analytics"])
@transaction_analytic_schema
class GetAnalyticForMonth(generics.GenericAPIView):
    """Get monthly analytics."""

    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get(self, request, *args, **kwargs) -> Response:
        """Get monthly cost or income analytics."""
        year: int = request.query_params.get("year", dt.now(UTC).year)
        type_tr: str = request.query_params.get("type", "expense")

        if not year:
            return Response(
                {"error": "Year is required."},
                status=400
            )

        try:
            year = int(year)
        except ValueError:
            return Response(
                {"error": "Year must be a valid integer."},
                status=400
            )

        analytics_service = MonthlyAnalyticsService()
        analytics = analytics_service.get_analytics(
            request.user.id,
            year,
            type_tr
        )
        analytics_list = list(analytics)
        serializer = FormattedMonthlyAnalyticsSerializer(
            analytics_list, many=True
        )
        return Response({"results": serializer.data})


@extend_schema(tags=["Analytics"])
class ForecastView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get(self, request, *args, **kwargs) -> Response:
        """Возвращает умный прогноз Cash Flow на конец месяца."""
        service = ForecastService(request.user)
        forecast = service.calculate()
        return Response(forecast)


@extend_schema(tags=["Analytics"])
class GetAnalyticForDay(generics.GenericAPIView):
    """Get daily analytics for a specific month."""

    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get(self, request, *args, **kwargs) -> Response:
        year = request.query_params.get("year", dt.now(UTC).year)
        month = request.query_params.get("month", dt.now(UTC).month)
        type_tr = request.query_params.get("type", "expense")

        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return Response(
                {"error": "Year and month must be valid integers."},
                status=400
            )

        analytics_service = DailyAnalyticsService()
        analytics = analytics_service.get_analytics(
            request.user.id,
            year,
            month,
            type_tr
        )

        return Response({"results": analytics})
