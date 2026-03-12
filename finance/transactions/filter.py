from typing import Any, Optional, Dict, List
from collections import defaultdict

import django_filters
from django.db.models import QuerySet

from .models import Transaction, Category
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
    Суммы родительских категорий включают все дочерние транзакции.
    """
    # Шаг 1: Получаем сырые данные транзакций
    transactions_data = fetch_transactions_with_categories(
        user, year, month, type_tr
    )
    
    # Шаг 2: Агрегируем суммы по категориям (только прямые транзакции)
    categories_aggregated = aggregate_category_totals(transactions_data)
    
    # Шаг 3: Добавляем структуру children (пока без пересчета сумм)
    categories_with_structure = link_children_to_parents(categories_aggregated)
    
    # Шаг 4: ПЕРЕСЧИТЫВАЕМ суммы с учетом иерархии (сумма = своя + всех детей)
    categories_with_totals = calculate_hierarchical_totals(
        categories_with_structure
    )
    
    # Шаг 5: Строим иерархическое дерево с правильными суммами
    return build_tree_from_roots(categories_with_totals)


def fetch_transactions_with_categories(
    user: CustomUser, 
    year: int, 
    month: int, 
    type_tr: str
) -> QuerySet:
    """
    Получает все транзакции пользователя за указанный 
    месяц с информацией о категориях.
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
    Агрегирует суммы транзакций по категориям (только прямые транзакции).
    Возвращает словарь {category_id: category_data}
    """
    categories = {}
    all_category_ids = set()  # Для отслеживания всех упомянутых категорий
    parent_ids = set()  # Для отслеживания родительских ID
    
    # Сначала собираем все ID категорий и родителей из транзакций
    for transaction in transactions:
        cat_id = transaction['category_id']
        all_category_ids.add(cat_id)
        
        parent_id = transaction['category__parent_id']
        if parent_id:
            parent_ids.add(parent_id)
    
    # Добавляем родительские категории, даже если у них нет своих транзакций
    all_category_ids.update(parent_ids)
    
    # Получаем информацию о категориях из базы
    categories_from_db = Category.objects.filter(
        id__in=all_category_ids
    ).select_related('parent')
    category_db_info = {}
    
    for cat in categories_from_db:
        category_db_info[cat.id] = {
            'name': cat.name,
            'parent_id': cat.parent_id if cat.parent else None,
            'parent_name': cat.parent.name if cat.parent else None,
        }
    
    # Инициализируем все категории
    for cat_id in all_category_ids:
        if cat_id in category_db_info:
            info = category_db_info[cat_id]
            categories[cat_id] = {
                'id': cat_id,
                'name': info['name'],
                'parent_id': info['parent_id'],
                'parent_name': info['parent_name'],
                'total_direct': 0,
                'total_with_children': 0,
                'children': []
            }
        else:
            # Если категория не найдена в БД, создаем заглушку
            categories[cat_id] = {
                'id': cat_id,
                'name': f"Category {cat_id}",
                'parent_id': None,
                'parent_name': None,
                'total_direct': 0,
                'total_with_children': 0,
                'children': []
            }
    
    # Теперь добавляем суммы из транзакций
    for transaction in transactions:
        cat_id = transaction['category_id']
        if cat_id in categories:
            categories[cat_id]['total_direct'] += float(
                transaction['amount'] or 0
            )
    return categories


def create_category_base_data(transaction: Dict) -> Dict[str, Any]:
    """
    Создает базовую структуру данных для категории на основе одной транзакции.
    """
    return {
        'id': transaction['category_id'],
        'name': transaction['category__name'],
        'parent_id': transaction['category__parent_id'],
        'parent_name': transaction['category__parent__name'],
        'total_direct': 0,  # Сумма только прямых транзакций этой категории
        'total_with_children': 0,  # Сумма с учетом всех детей (будет вычислена позже)
        'children': []
    }


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
    
    # Добавляем детей к родителям (без сортировки пока)
    for parent_id, children in children_by_parent.items():
        if parent_id in categories:
            categories[parent_id]['children'] = children
    
    return categories


def calculate_hierarchical_totals(
    categories: Dict[int, Dict[str, Any]]
) -> Dict[int, Dict[str, Any]]:
    """
    Рекурсивно вычисляет суммы для каждой категории с учетом всех дочерних.
    total_with_children = total_direct + сумма всех total_with_children детей
    """
    # Множество для отслеживания обработанных категорий
    processed: Set[int] = set()
    
    def calculate_node_total(cat_id: int) -> float:
        """Рекурсивно вычисляет сумму для узла и его детей."""
        if cat_id in processed:
            return categories[cat_id]['total_with_children']
        
        cat_data = categories[cat_id]
        total = cat_data['total_direct']
        
        # Добавляем суммы всех детей
        for child in cat_data['children']:
            total += calculate_node_total(child['id'])
        
        cat_data['total_with_children'] = total
        processed.add(cat_id)
        return total
    
    # Запускаем вычисление для всех корневых категорий
    for cat_id, cat_data in categories.items():
        if cat_id not in processed:
            calculate_node_total(cat_id)
    
    return categories


def build_tree_from_roots(
    categories: Dict[int, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Рекурсивно строит дерево, используя вычисленные суммы с детьми.
    """
    def build_subtree(parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Внутренняя рекурсивная функция для построения поддерева."""
        subtree = []
        
        for cat_data in categories.values():
            if cat_data['parent_id'] == parent_id:
                # Рекурсивно получаем детей для этой категории
                children = build_subtree(cat_data['id'])
                
                # Создаем чистую структуру категории для вывода
                clean_category = create_clean_category(cat_data, children)
                subtree.append(clean_category)
        
        # Сортируем поддерево по убыванию суммы (с учетом детей)
        subtree.sort(key=lambda x: x['total'], reverse=True)
        return subtree
    
    return build_subtree()


def create_clean_category(
    category_data: Dict[str, Any], 
    children: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Создает чистую структуру категории для сериализации.
    Использует total_with_children как итоговую сумму.
    """
    clean_cat = {
        'id': category_data['id'],
        'name': category_data['name'],
        'total': category_data['total_with_children'],
        'total_direct': category_data['total_direct'],
        'children': children
    }
    
    # Добавляем информацию о родителе, если он есть
    if category_data.get('parent_name'):
        clean_cat['parent'] = {
            'id': category_data['parent_id'],
            'name': category_data['parent_name']
        }
    
    return clean_cat
