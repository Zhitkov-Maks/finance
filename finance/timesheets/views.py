import os
import requests
from django.http import HttpRequest, HttpResponse

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
    BasicAuthentication,
)
from rest_framework.permissions import IsAuthenticated

from .schemas import (
    ManyAddSchemas,
    StatisticForMonthSchema,
    TimeSheetsForDaySchema,
    TimeSheetsSchema,
    TimeSheetsSettingsSchema,
    StatisticForYearSchema
)

HOST = os.getenv('FINANCE_FASTAPI_URL', 'http://fastapi:8080')

BASE_URL = f"{HOST}/api/v2/"


@extend_schema(tags=["TimeSheetsSettings"])
@TimeSheetsSettingsSchema
class GetTimesheetsSettings(generics.GenericAPIView):
    """A class for working with user settings."""

    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["get", "post", "delete"]

    def get(self, request, *args, **kwargs):
        """Get monthly cost or income analytics."""
        user = request.user.id
        external_response = requests.get(url=(BASE_URL + f"settings/?user_id={user}"))

        return HttpResponse(
            external_response.content,
            content_type='application/json',
            status=external_response.status_code
        )

    def post(self, request):
        user = request.user.id
        data = request.data
        response = requests.post(
            url=f"{BASE_URL}settings/?user_id={user}",
            json=data if isinstance(data, dict) else dict(data),
            timeout=30
        )
        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )

    def delete(self, request, *args, **kwargs):
        user = request.user.id
        response = requests.delete(
            url=(BASE_URL + f"settings/?user_id={user}")
        )
        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )


@extend_schema(tags=["Shifts"])
@TimeSheetsSchema
class GetShifts(generics.GenericAPIView):
    """A class for working with user settings."""

    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["get", "post", "put"]

    def get(self, request: HttpRequest):
        """Get monthly cost or income analytics."""
        user = request.user.id
        data = request.GET.dict()
        url = f"{BASE_URL}shifts/?user_id={user}&year={data["year"]}&month={data["month"]}"
        response = requests.get(url=url)

        return HttpResponse(
            response.content,
            content_type='application/json',
            status=response.status_code
        )

    def post(self, request):
        return self._handle_shifts_request(request)

    def put(self, request):
        return self._handle_shifts_request(request)

    def _handle_shifts_request(self, request):
        user = request.user.id
        data = request.data
        response = requests.post(
            url=f"{BASE_URL}shifts/?user_id={user}",
            json=data if isinstance(data, dict) else dict(data),
            timeout=30
        )
        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )


@extend_schema(tags=["ShiftsForDay"])
@TimeSheetsForDaySchema
class GetShiftsForDay(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["get", "post", "delete"]

    def get(self, request,  day_id: str):
        print(f"{BASE_URL}shifts/{day_id}/")
        response = requests.get(url=f"{BASE_URL}shifts/{day_id}/")
        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )

    def post(self, request, day_id):
        data = request.GET.dict()
        user_id = request.user.id
        print(data)
        url = f"{BASE_URL}shifts/{day_id}/award/?user_id={user_id}&count_operations={data['count_operations']}"
        response = requests.post(url=url)
        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )

    def delete(self, request, day_id):
        response = requests.delete(url=f"{BASE_URL}shifts/{day_id}/")
        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )


@extend_schema(tags=["ShiftsManyAdd"])
@ManyAddSchemas
class ManyAddShifts(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["post"]

    def post(self, request):
        data, user_id = request.data, request.user.id
        response = requests.post(
            url=f"{BASE_URL}shifts/many/?user_id={user_id}",
            json=data if isinstance(data, dict) else dict(data),
            timeout=30
        )

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )


@extend_schema(tags=["Statistic"])
@StatisticForMonthSchema
class StatisticForMonth(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["get"]

    def get(self, request):
        data = request.GET.dict()
        user_id, year, month = request.user.id, data["year"], data["month"]
        response = requests.get(
            url=f"{BASE_URL}statistic/month/?user_id={user_id}&year={year}&month={month}"
        )

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )


@extend_schema(tags=["Statistic"])
@StatisticForYearSchema
class StatisticForYear(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["get"]

    def get(self, request):
        data = request.GET.dict()
        user_id, year = request.user.id, data["year"]
        response = requests.get(
            url=f"{BASE_URL}statistic/year/?user_id={user_id}&year={year}"
        )

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )
