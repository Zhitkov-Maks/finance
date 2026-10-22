from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Insight
from .serializers import InsightSerializer


@extend_schema(tags=["Insights"])
class InsightListView(generics.ListAPIView):
    serializer_class = InsightSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get_queryset(self):
        qs = Insight.objects.filter(user=self.request.user)
        if self.request.query_params.get("active") == "1":
            qs = qs.filter(is_dismissed=False)
        return qs.order_by("-created_at")


@extend_schema(tags=["Insights"])
class InsightDismissView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def post(self, request, pk):
        Insight.objects.filter(user=request.user, pk=pk).update(is_dismissed=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
