from typing import Any, Optional, Dict, List
from collections import defaultdict

import django_filters
from django.db.models import QuerySet

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
    user: CustomUser, year: int, month: int, type_tr: str
) -> List[Dict[str, Any]]:
    """
    Главная функция: получает статистику по категориям в виде дерева.
    """
    # Шаг 1: Получаем сырые данные транзакций
    transactions_data = fetch_transactions_with_categories(
        user, year, month, type_tr
    )
    
    # Шаг 2: Агрегируем суммы по категориям
    categories_aggregated = aggregate_category_totals(transactions_data)
    
    # Шаг 3: Строим иерархическое дерево
    return build_category_tree(categories_aggregated)


def fetch_transactions_with_categories(
    user: CustomUser, 
    year: int, 
    month: int, 
    type_tr: str
) -> QuerySet:
    """
    Получает все транзакции пользователя за 
    указанный месяц с информацией о категориях.
    """
    return (Transaction.objects
        .filter(
            user=user,
            create_at__year=year,
            create_at__month=month,
            category__type_transaction=type_tr
        )
        .select_related('category')
        .values(
            'category_id',
            'category__name',
            'category__parent_id',
            'category__parent__name',
            'amount'
        )
    )


def aggregate_category_totals(
    transactions: QuerySet
) -> Dict[int, Dict[str, Any]]:
    """
    Агрегирует суммы транзакций по категориям.
    Возвращает словарь {category_id: category_data}
    """
    categories = {}
    
    for transaction in transactions:
        cat_id = transaction['category_id']
        
        if cat_id not in categories:
            categories[cat_id] = create_category_base_data(transaction)
        
        # Добавляем сумму транзакции к общему итогу категории
        categories[cat_id]['total'] += float(transaction['amount'] or 0)
    
    return categories


def create_category_base_data(transaction: Dict) -> Dict[str, Any]:
    """
    Создает базовую структуру данных для 
    категории на основе одной транзакции.
    """
    return {
        'id': transaction['category_id'],
        'name': transaction['category__name'],
        'parent_id': transaction['category__parent_id'],
        'parent_name': transaction['category__parent__name'],
        'total': 0,
        'children': []
    }


def build_category_tree(
    categories: Dict[int, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Строит иерархическое дерево категорий из плоского словаря.
    Возвращает список корневых категорий с вложенными детьми.
    """
    # Сначала добавляем детей к родителям
    categories_with_children = link_children_to_parents(categories)
    
    # Затем собираем дерево, начиная с корневых категорий (parent_id = None)
    return build_tree_from_roots(categories_with_children)


def link_children_to_parents(
    categories: Dict[int, Dict[str, Any]]
) -> Dict[int, Dict[str, Any]]:
    """
    Связывает дочерние категории с их родителями.
    Возвращает тот же словарь, но с заполненными полями children.
    """
    # Группируем категории по parent_id
    children_by_parent = defaultdict(list)
    
    for cat_id, cat_data in categories.items():
        parent_id = cat_data['parent_id']
        if parent_id:
            children_by_parent[parent_id].append(cat_data)
    
    # Добавляем детей к родителям
    for parent_id, children in children_by_parent.items():
        if parent_id in categories:
            # Сортируем детей по сумме перед добавлением
            categories[parent_id]['children'] = sorted(
                children, 
                key=lambda x: x['total'], 
                reverse=True
            )
    
    return categories


def build_tree_from_roots(
    categories: Dict[int, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Рекурсивно строит дерево, начиная с корневых категорий.
    """
    def build_subtree(parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Внутренняя рекурсивная функция для построения поддерева.
        """
        subtree = []
        
        for cat_data in categories.values():
            if cat_data['parent_id'] == parent_id:
                # Рекурсивно получаем детей для этой категории
                children = build_subtree(cat_data['id'])
                if children:
                    cat_data['children'] = children
                
                # Создаем чистую структуру категории для вывода
                clean_category = create_clean_category(cat_data)
                subtree.append(clean_category)
        
        # Сортируем поддерево по убыванию суммы
        subtree.sort(key=lambda x: x['total'], reverse=True)
        return subtree
    
    return build_subtree()


def create_clean_category(category_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Создает чистую структуру категории для сериализации.
    Убирает служебные поля и форматирует parent информацию.
    """
    clean_cat = {
        'id': category_data['id'],
        'name': category_data['name'],
        'total': category_data['total'],
        'children': category_data.get('children', [])
    }
    
    # Добавляем информацию о родителе, если он есть
    if category_data.get('parent_name'):
        clean_cat['parent'] = {
            'id': category_data['parent_id'],
            'name': category_data['parent_name']
        }
    
    return clean_cat
