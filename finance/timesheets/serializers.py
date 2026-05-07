from decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers


class TimeSheetsRequest(serializers.Serializer):
    date = serializers.CharField(help_text="Дата в формате 'гггг-мм-дд")
    time = serializers.FloatField(help_text="Отработанное время.")


class TimeSheetsSettingsRequestSerializer(serializers.Serializer):
    """Сериализатор для создания/обновления настроек."""
    price_time = serializers.FloatField(
        help_text="Стоимость обычного времени"
    )
    price_overtime = serializers.FloatField(
        help_text="Стоимость сверхурочного времени"
    )
    price_cold = serializers.FloatField(
        help_text="Стоимость работы в холодных условиях"
    )
    price_award = serializers.FloatField(
        help_text="Размер премии"
    )

    def validate(self, data):
        """Дополнительная валидация данных."""
        for field in ['price_time', 'price_overtime', 'price_cold', 'price_award']:
            if data[field] < 0:
                raise serializers.ValidationError(
                    {field: "Значение не может быть отрицательным."}
                )
        return data


class TimeSheetsSettingsResponseSerializer(serializers.Serializer):
    """Сериализатор для ответа с настройками пользователя."""
    price_time = serializers.FloatField(read_only=True)
    price_overtime = serializers.FloatField(read_only=True)
    price_cold = serializers.FloatField(read_only=True)
    price_award = serializers.FloatField(read_only=True)

class SuccessResponseSerializer(serializers.Serializer):
    """Общий сериализатор успешного ответа."""
    result = serializers.BooleanField(default=True)

class NotFoundResponseSerializer(serializers.Serializer):
    """Сериализатор ответа при отсутствии данных."""
    detail = serializers.DictField(child=serializers.CharField())

class ValidationErrorSerializer(serializers.Serializer):
    """Сериализатор ошибок валидации."""

    class Meta:
        ref_name = 'TimesheetsValidationError'

    loc = serializers.ListField(
        child=serializers.CharField(),
        help_text="Путь к полю с ошибкой"
    )
    msg = serializers.CharField(help_text="Сообщение об ошибке")
    type = serializers.CharField(help_text="Тип ошибки")
    input = serializers.CharField(help_text="Введённые данные")
    ctx = serializers.DictField(
        required=False,
        allow_null=True,
        help_text="Дополнительные контекстные данные"
    )

class ValidationErrorsResponseSerializer(serializers.Serializer):
    """Сериализатор массива ошибок валидации."""
    detail = serializers.ListField(child=ValidationErrorSerializer())


class ValuteSerializer(serializers.Serializer):
    dollar = serializers.FloatField()
    euro = serializers.FloatField()
    yena = serializers.FloatField()
    som = serializers.FloatField()


class DayStatsSerializer(serializers.Serializer):
    day_id = serializers.CharField(max_length=255)
    base_hours = serializers.IntegerField()
    date = serializers.DateTimeField(input_formats=['%Y-%m-%d %H:%M:%S'])
    earned = serializers.IntegerField()
    earned_cold = serializers.IntegerField(allow_null=True, required=False)
    earned_hours = serializers.IntegerField()
    period = serializers.IntegerField()
    valute = ValuteSerializer()
    award_amount = serializers.IntegerField(allow_null=True, required=False)
    count_operations = serializers.IntegerField(allow_null=True, required=False)


class ShiftsRequestSerializer(serializers.Serializer):
    hours = serializers.IntegerField(
        min_value=1,
        max_value=24,
        help_text="Количество часов (1-24)"
    )
    dates = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=False,
        help_text="Список дат в формате YYYY-MM-DD"
    )

    def validate(self, data):
        # Уникальные даты
        if len(data['dates']) != len(set(data['dates'])):
            raise serializers.ValidationError(
                {"dates": "Даты не должны повторяться"}
            )
        return data


class TotalStatsSerializer(serializers.Serializer):
    total_hours = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_earned = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_award = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    dollar = serializers.DecimalField(max_digits=12, decimal_places=2)
    euro = serializers.DecimalField(max_digits=12, decimal_places=2)
    yena = serializers.DecimalField(max_digits=12, decimal_places=2)
    som = serializers.DecimalField(max_digits=15, decimal_places=2)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in ['dollar', 'euro', 'yena', 'som']:
            if data[field]:
                data[field] = float(Decimal(str(data[field])).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                ))
        return data


class PeriodStatsSerializer(serializers.Serializer):
    total_base_hours = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_earned = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_earned_hours = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_earned_cold = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    total_award = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    total_operations = serializers.IntegerField(required=False)
    total_overtime = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    total_hours_overtime = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    dollar = serializers.DecimalField(max_digits=12, decimal_places=2)
    euro = serializers.DecimalField(max_digits=12, decimal_places=2)
    yena = serializers.DecimalField(max_digits=12, decimal_places=2)
    som = serializers.DecimalField(max_digits=12, decimal_places=2)


class FullStatsSerializer(serializers.Serializer):
    period_one = PeriodStatsSerializer()
    period_two = PeriodStatsSerializer()
    total = PeriodStatsSerializer()
