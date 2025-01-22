import django_filters
from .models import Income

class IncomeFilter(django_filters.FilterSet):
    create_at = django_filters.DateFromToRangeFilter()
    account_name = django_filters.CharFilter(field_name='account__name', lookup_expr='icontains')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')

    class Meta:
        model = Income
        fields = ['create_at', 'account_name', "category_name"]
