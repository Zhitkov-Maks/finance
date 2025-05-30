import django_filters
from django.db.models import QuerySet, Sum

from .models import Income

class IncomeFilter(django_filters.FilterSet):
    create_at = django_filters.DateFromToRangeFilter()
    account_name = django_filters.CharFilter(
        field_name='account__name', lookup_expr='icontains'
    )
    category_name = django_filters.CharFilter(
        field_name='category__name', lookup_expr='icontains'
    )
    amount_gte = django_filters.NumberFilter(
        field_name='amount', lookup_expr='gte'
    )

    amount_lte = django_filters.NumberFilter(
        field_name='amount', lookup_expr='lte'
    )

    class Meta:
        model = Income
        fields = [
            'create_at',
            'account_name',
            "category_name",
            "amount_gte",
            "amount_lte"
        ]


def get_category_income_statistics(user, year, month) -> QuerySet:
    """
    Функция для получения статистики за переданный месяц и год.
    :param user: Пользователь по которому идет сбор статистики.
    :param year: Год для статистики.
    :param month: Месяц для статистики.
    :return Queryset: Список с суммой расхода по категориям
                        отсортированные в порядке убывания.
    """
    return (
        Income.objects
        .filter(user=user, create_at__year=year, create_at__month=month)
        .values('category__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('-total_amount')
    )
