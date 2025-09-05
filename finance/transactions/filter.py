import django_filters
from django.db.models import QuerySet, Sum

from .models import Transaction
from app_user.models import CustomUser


class TransactionFilter(django_filters.FilterSet):
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
        model = Transaction
        fields = [
            'create_at',
            'account_name',
            "category_name",
            "amount_gte",
            "amount_lte"
        ]


def get_category_statistics(
    user: CustomUser,
    year: int,
    month: int,
    type_tr: str
) -> QuerySet:
    """
    Функция для получения статистики за переданный месяц и год.
    :param user: Пользователь по которому идет сбор статистики.
    :param year: Год для статистики.
    :param month: Месяц для статистики.
    :return Queryset: Список с суммой расхода по категориям
                        отсортированные в порядке убывания.
    """
    return (
        Transaction.objects
        .filter(
            user=user,
            create_at__year=year,
            create_at__month=month,
            category__type_transaction=type_tr
        )
        .values('category__name')
        .annotate(total_amount=Sum('amount'))
        .order_by('-total_amount')
    )
