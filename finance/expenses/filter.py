import django_filters
from django.db.models import Sum, QuerySet

from .models import Expense

class IncomeFilter(django_filters.FilterSet):
    create_at = django_filters.DateFromToRangeFilter()
    account_name = django_filters.CharFilter(field_name='account__name', lookup_expr='icontains')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')

    class Meta:
        model = Expense
        fields = ['create_at', 'account_name', "category_name"]


def get_category_expense_statistics(user, year, month) -> QuerySet:
    """
    Функция для получения статистики за переданный месяц и год.
    :param user: Пользователь по которому идет сбор статистики.
    :param year: Год для статистики.
    :param month: Месяц для статистики.
    :return Queryset: Список с суммой расхода по категориям
                        отсортированные в порядке убывания.
    """
    return (
        Expense.objects
        .filter(user=user, create_at__year=year, create_at__month=month)
        .values('category__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('-total_amount')
    )
