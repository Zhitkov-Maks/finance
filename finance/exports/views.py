import re

from django.http import FileResponse, JsonResponse
from django.utils import timezone
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .services import ExportService


def _safe_filename(user, ext: str) -> str:
    """
    Строит безопасное имя файла для Content-Disposition.

    CustomUser: USERNAME_FIELD = 'email', username = None — email единственный
    осмысленный идентификатор. Приводим к [\\w\\-], чтобы не сломать заголовок
    HTTP (email содержит '@' и '.').
    """
    raw = (getattr(user, "email", None) or "").strip() or f"user{user.id}"
    slug = re.sub(r"[^\w\-]", "_", raw)
    ts = timezone.now().strftime("%Y%m%d_%H%M%S")
    return f"finances_{slug}_{ts}.{ext}"


class ExportView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (
        TokenAuthentication,
        BasicAuthentication,
        SessionAuthentication,
    )

    def get(self, request):
        fmt = request.query_params.get("format", "json").lower()
        if fmt == "info":
            return JsonResponse(ExportService(request.user).export_info())

        if fmt not in ("json", "csv"):
            raise ValidationError({"format": "Разрешены: json, csv, info"})

        service = ExportService(request.user)

        if fmt == "csv":
            buffer = service.export_csv_zip()
            size = buffer.getbuffer().nbytes
            response = FileResponse(
                buffer,
                as_attachment=True,
                filename=_safe_filename(request.user, "zip"),
                content_type="application/zip",
            )
            response["Content-Length"] = str(size)
            return response

        data = service.export_json()
        response = JsonResponse(
            data,
            json_dumps_params={"ensure_ascii": False, "indent": 2},
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{_safe_filename(request.user, "json")}"'
        )
        return response
