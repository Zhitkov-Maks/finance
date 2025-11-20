from rest_framework import serializers


class FormattedMonthlyAnalyticsSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    period = serializers.SerializerMethodField()
    month_name = serializers.SerializerMethodField()

    # Basic metrics
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = serializers.IntegerField()
    avg_amount = serializers.DecimalField(max_digits=15, decimal_places=2)

    # Comparative metrics
    first_month_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    prev_month_amount = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2,
        default=0
    )

    # Percentage changes
    change_vs_first_percent = serializers.SerializerMethodField()
    change_vs_prev_percent = serializers.SerializerMethodField()

    # Absolute changes
    absolute_change_vs_first = serializers.SerializerMethodField()
    absolute_change_vs_prev = serializers.SerializerMethodField()

    # Trends and statuses
    trend_vs_first = serializers.SerializerMethodField()
    trend_vs_prev = serializers.SerializerMethodField()
    is_first_month = serializers.SerializerMethodField()
    
    def get_period(self, obj):
        return f"{obj['year']}-{obj['month']:02d}"

    def get_month_name(self, obj):
        months = {
            1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
            5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
            9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
        }
        return months.get(obj['month'], 'Неизвестно')

    def get_change_vs_first_percent(self, obj):
        percent = obj.get('change_vs_first_percent', 0)
        return round(percent, 2) if percent is not None else 0

    def get_change_vs_prev_percent(self, obj):
        percent = obj.get('change_vs_prev_percent')
        return round(percent, 2) if percent is not None else 0

    def get_absolute_change_vs_first(self, obj):
        return round(obj['total_amount'] - obj['first_month_amount'], 2)

    def get_absolute_change_vs_prev(self, obj):
        prev_amount = obj.get('prev_month_amount')
        if prev_amount is not None:
            return round(obj['total_amount'] - prev_amount, 2)
        return 0

    def get_trend_vs_first(self, obj):
        change = obj.get('change_vs_first_percent', 0)
        return self._get_trend_description(change)

    def get_trend_vs_prev(self, obj):
        change = obj.get('change_vs_prev_percent')
        if change is not None:
            return self._get_trend_description(change)
        return 'no_data'

    def get_is_first_month(self, obj):
        return obj.get('prev_month_amount') is None

    def _get_trend_description(self, change_percent):
        if change_percent is None:
            return '⇝'
        elif change_percent > 10:
            return '⇈'
        elif change_percent > 0:
            return '⇑'
        elif change_percent == 0:
            return '⇝'
        elif change_percent > -10:
            return '⇓'
        else:
            return '⇊'
