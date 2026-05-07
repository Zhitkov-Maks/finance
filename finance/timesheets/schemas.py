from drf_spectacular.utils import OpenApiParameter, extend_schema_view, \
    extend_schema
from .serializers import (
    DayStatsSerializer,
    FullStatsSerializer,
    ShiftsRequestSerializer,
    TimeSheetsRequest,
    TimeSheetsSettingsRequestSerializer,
    TimeSheetsSettingsResponseSerializer,
    SuccessResponseSerializer,
    NotFoundResponseSerializer,
    TotalStatsSerializer,
    ValidationErrorsResponseSerializer
)

TimeSheetsSettingsSchema = extend_schema_view(
    get=extend_schema(
        description="Получить настройки пользователя",
        responses={
            200: TimeSheetsSettingsResponseSerializer,
            404: NotFoundResponseSerializer,
            422: ValidationErrorsResponseSerializer,
        },
    ),
    post=extend_schema(
        description="Создать или обновить настройки пользователя",
        request=TimeSheetsSettingsRequestSerializer,
        responses={
            201: SuccessResponseSerializer,
            400: ValidationErrorsResponseSerializer,
            422: ValidationErrorsResponseSerializer,
        },
    ),
    delete=extend_schema(
        description="Удалить настройки пользователя",
        responses={
            204: None,
            404: NotFoundResponseSerializer,
        }
    )
)

TimeSheetsSchema = extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "year", int,
                description="Год",
                required=True
            ),
            OpenApiParameter(
                "month", int,
                description="Месяц",
                required=True
            )
        ],
        description="Получение списка смен за месяц."
    ),
    post=extend_schema(
        request=TimeSheetsRequest,
        description="Создать новую запись о рабочей смене.",
        responses={
            201: SuccessResponseSerializer,
            404: NotFoundResponseSerializer,
            422: ValidationErrorsResponseSerializer
        }
    ),
    put=extend_schema(
        request=TimeSheetsRequest,
        description="Обновить запись о рабочей смене.",
        responses={
            201: SuccessResponseSerializer,
            404: NotFoundResponseSerializer,
            422: ValidationErrorsResponseSerializer
        }
    )
)


TimeSheetsForDaySchema = extend_schema_view(
    get=extend_schema(
        description="Получение списка смен за месяц.",
        responses={
            200: DayStatsSerializer,
            404: NotFoundResponseSerializer,
        }
    ),
    post=extend_schema(
        description="Создать новую запись о рабочей смене.",
        parameters=[
            OpenApiParameter(
                "count_operations", int,
                description="Количество операций",
                required=True
            )
        ],
        responses={
            201: DayStatsSerializer,
            422: ValidationErrorsResponseSerializer
        }
    ),
    delete=extend_schema(
        description="Удалить смену по идентификатору.",
        responses={
            204: None,
            404: NotFoundResponseSerializer,
        }
    )
)


ManyAddSchemas = extend_schema_view(
    post=extend_schema(
        description="Запрос на добавление смен за месяц.",
        request=ShiftsRequestSerializer,
        responses={
            201: SuccessResponseSerializer,
            400: ValidationErrorsResponseSerializer
        }
    )
)


StatisticForMonthSchema = extend_schema_view(
    get=extend_schema(
        description="Получение статистики за год.",
        parameters=[
            OpenApiParameter(
                "year", int,
                description="Год для статистики",
                required=True
            ),
            OpenApiParameter(
                "month", int,
                description="Месяц для статистики",
                required=True
            )
        ],
        responses={
            200: FullStatsSerializer,
            400: ValidationErrorsResponseSerializer
        }
    )
)

StatisticForYearSchema = extend_schema_view(
    get=extend_schema(
        description="Получение статистики за год.",
        parameters=[
            OpenApiParameter(
                "year", int,
                description="Год для статистики",
                required=True
            )
        ],
        responses={
            200: TotalStatsSerializer,
            400: ValidationErrorsResponseSerializer
        }
    )
)
