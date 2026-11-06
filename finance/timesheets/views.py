import os

import requests
from django.core.cache import cache
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.permissions import IsAuthenticated

from .cache import CACHE_TTL, invalidate_timesheets_cache, make_timesheets_key
from .schemas import (
    ManyAddSchemas,
    StatisticForMonthSchema,
    StatisticForYearSchema,
    TimeSheetsForDaySchema,
    TimeSheetsSchema,
    TimeSheetsSettingsSchema,
    VacationAddSchemas,
)

HOST = os.getenv("FINANCE_FASTAPI_URL", "http://fastapi:8080")
BASE_URL = f"{HOST}/api/v1/"


def _request_fastapi(method: str, url: str, **kwargs) -> requests.Response:
    """Хелпер для безопасного вызова FastAPI с таймаутом."""
    try:
        return requests.request(method, url, timeout=10, **kwargs)
    except requests.RequestException as e:
        from rest_framework.exceptions import APIException

        raise APIException(f"Service unavailable: {e}")


@extend_schema(tags=["TimeSheetsSettings"])
@TimeSheetsSettingsSchema
class GetTimesheetsSettings(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["get", "post", "delete"]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        cache_key = make_timesheets_key(user_id, "settings")

        # 1. Пробуем достать из кэша
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            response = HttpResponse(
                cached_data, content_type="application/json", status=200
            )
            response["X-Cache"] = "HIT"
            return response

        # 2. Если нет — идем в FastAPI
        external_response = _request_fastapi(
            "get", f"{BASE_URL}settings/?user_id={user_id}"
        )

        if external_response.status_code == 200:
            cache.set(cache_key, external_response.content, timeout=CACHE_TTL)

        response = HttpResponse(
            external_response.content,
            content_type="application/json",
            status=external_response.status_code,
        )
        response["X-Cache"] = "MISS"
        return response

    def post(self, request):
        user_id = request.user.id
        data = request.data
        response = _request_fastapi(
            "post",
            f"{BASE_URL}settings/?user_id={user_id}",
            json=data if isinstance(data, dict) else dict(data),
        )

        # Сбрасываем кэш при успешном изменении
        if response.status_code < 400:
            invalidate_timesheets_cache(user_id)

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )

    def delete(self, request, *args, **kwargs):
        user_id = request.user.id
        response = _request_fastapi("delete", f"{BASE_URL}settings/?user_id={user_id}")

        # Сбрасываем кэш при успешном удалении
        if response.status_code < 400:
            invalidate_timesheets_cache(user_id)

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )


@extend_schema(tags=["Shifts"])
@TimeSheetsSchema
class GetShifts(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["get", "post", "put"]

    def get(self, request):
        user_id = request.user.id
        data = request.GET.dict()
        year = data.get("year")
        month = data.get("month")

        cache_key = make_timesheets_key(user_id, "shifts", year, month)

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            response = HttpResponse(
                cached_data, content_type="application/json", status=200
            )
            response["X-Cache"] = "HIT"
            return response

        url = f"{BASE_URL}shifts/?user_id={user_id}&year={year}&month={month}"
        external_response = _request_fastapi("get", url)

        if external_response.status_code == 200:
            cache.set(cache_key, external_response.content, timeout=CACHE_TTL)

        response = HttpResponse(
            external_response.content,
            content_type="application/json",
            status=external_response.status_code,
        )
        response["X-Cache"] = "MISS"
        return response

    def post(self, request):
        return self._handle_shifts_request(request)

    def put(self, request):
        return self._handle_shifts_request(request)

    def _handle_shifts_request(self, request):
        user_id = request.user.id
        data = request.data
        response = _request_fastapi(
            "post",
            f"{BASE_URL}shifts/?user_id={user_id}",
            json=data if isinstance(data, dict) else dict(data),
        )

        if response.status_code < 400:
            invalidate_timesheets_cache(user_id)

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
    http_method_names = ["get", "post", "put", "delete"]

    def get(self, request, day_id: str):
        user_id = request.user.id
        cache_key = make_timesheets_key(user_id, "shift", day_id)

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            response = HttpResponse(
                cached_data, content_type="application/json", status=200
            )
            response["X-Cache"] = "HIT"
            return response

        external_response = _request_fastapi("get", f"{BASE_URL}shifts/{day_id}/")

        if external_response.status_code == 200:
            cache.set(cache_key, external_response.content, timeout=CACHE_TTL)

        response = HttpResponse(
            external_response.content,
            status=external_response.status_code,
            content_type="application/json",
        )
        response["X-Cache"] = "MISS"
        return response

    def post(self, request, day_id):
        user_id = request.user.id
        data = request.GET.dict()
        url = (
            f"{BASE_URL}shifts/{day_id}/award/?user_id={user_id}"
            f"&count_operations={data.get('count_operations', 0)}"
            f"&type_operations={data.get('type_operations', 0)}"
        )
        response = _request_fastapi("post", url)

        if response.status_code < 400:
            invalidate_timesheets_cache(user_id)

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )

    def put(self, request, day_id):
        user_id = request.user.id
        data = request.GET.dict()
        url = (
            f"{BASE_URL}shifts/{day_id}"
            f"/hours/?user_id={user_id}&hours={data.get('hours', 0)}"
        )
        response = _request_fastapi("put", url)

        if response.status_code < 400:
            invalidate_timesheets_cache(user_id)

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )

    def delete(self, request, day_id):
        user_id = request.user.id
        response = _request_fastapi("delete", f"{BASE_URL}shifts/{day_id}/")

        if response.status_code < 400:
            invalidate_timesheets_cache(user_id)

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
        response = _request_fastapi(
            "post",
            f"{BASE_URL}shifts/many/?user_id={user_id}",
            json=data if isinstance(data, dict) else dict(data),
        )

        if response.status_code < 400:
            invalidate_timesheets_cache(user_id)

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
        user_id = request.user.id
        year = data.get("year")
        month = data.get("month")

        cache_key = make_timesheets_key(user_id, "stats", year, month)

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            response = HttpResponse(
                cached_data, content_type="application/json", status=200
            )
            response["X-Cache"] = "HIT"
            return response

        response = _request_fastapi(
            "get",
            f"{BASE_URL}statistic/month/?user_id={user_id}&year={year}&month={month}",
        )

        if response.status_code == 200:
            cache.set(cache_key, response.content, timeout=CACHE_TTL)

        http_resp = HttpResponse(
            response.content,
            status=response.status_code,
            content_type="application/json",
        )
        http_resp["X-Cache"] = "MISS"
        return http_resp


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
        user_id = request.user.id
        year = data.get("year")

        cache_key = make_timesheets_key(user_id, "stats", year)

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            response = HttpResponse(
                cached_data, content_type="application/json", status=200
            )
            response["X-Cache"] = "HIT"
            return response

        response = _request_fastapi(
            "get", f"{BASE_URL}statistic/year/?user_id={user_id}&year={year}"
        )

        if response.status_code == 200:
            cache.set(cache_key, response.content, timeout=CACHE_TTL)

        http_resp = HttpResponse(
            response.content,
            status=response.status_code,
            content_type="application/json",
        )
        http_resp["X-Cache"] = "MISS"
        return http_resp


@extend_schema(tags=["Vacation"])
@VacationAddSchemas
class VacationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )
    http_method_names = ["post"]

    def post(self, request):
        data, user_id = request.data, request.user.id
        response = _request_fastapi(
            "post",
            f"{BASE_URL}shifts/vacation/?user_id={user_id}",
            json={
                "start_date": data.get("start_date"),
                "number_of_days": data.get("number_of_days"),
                "type_days": data.get("type_days"),
            },
        )

        if response.status_code < 400:
            invalidate_timesheets_cache(user_id)

        return HttpResponse(
            response.content,
            status=response.status_code,
            content_type='application/json',
        )
