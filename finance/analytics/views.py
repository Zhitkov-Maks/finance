from datetime import datetime as dt, UTC

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
    BasicAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import FormattedMonthlyAnalyticsSerializer

from .filter import MonthlyAnalyticsService
from .schemas import transaction_analytic_schema


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
