from collections import defaultdict
from typing import Any, Dict, List, Optional, Set

import django_filters
from app_user.models import CustomUser
from django.db.models import QuerySet

from .models import Category, Transaction


class TransactionFilter(django_filters.FilterSet):
    create_at = django_filters.DateFromToRangeFilter()
    account_name = django_filters.CharFilter(
        field_name="account__name", lookup_expr="icontains"
    )
    category_name = django_filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )

    category_id = django_filters.NumberFilter(field_name="category_id")
    category_isnull = django_filters.BooleanFilter(
        field_name="category", lookup_expr="isnull"
    )

    amount_gte = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    amount_lte = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = [
            "create_at",
            "account_name",
            "category_name",
            "category_id",
            "category_isnull",
            "amount_gte",
            "amount_lte",
        ]


def get_category_statistics(
    user: CustomUser, year: int, month: int, type_tr: str
) -> List[Dict[str, Any]]:
    """
    Главная функция: получает статистику по категориям в виде дерева.
    Суммы родительских категорий включают все дочерние транзакции.
    """
    transactions_data = fetch_transactions_with_categories(user, year, month, type_tr)
    categories_aggregated = aggregate_category_totals(transactions_data)
    categories_with_structure = link_children_to_parents(categories_aggregated)
    categories_with_totals = calculate_hierarchical_totals(categories_with_structure)
    return build_tree_from_roots(categories_with_totals)


def fetch_transactions_with_categories(
    user: CustomUser, year: int, month: int, type_tr: str
) -> QuerySet:
    """
    Получает транзакции за месяц. Фильтруем по type_transaction самой транзакции!
    """
    return (
        Transaction.objects.filter(
            user=user,
            create_at__year=year,
            create_at__month=month,
            type_transaction=type_tr,
        )
        .select_related("category")
        .values(
            "category_id",
            "category__name",
            "category__parent_id",
            "category__parent__name",
            "amount",
        )
    )


def aggregate_category_totals(transactions: QuerySet) -> Dict[int, Dict[str, Any]]:
    """
    Агрегирует суммы транзакций по категориям.
    Транзакции без категории (category_id=None)
    сваливаем в виртуальную категорию с ID = 0.
    """
    categories = {}
    all_category_ids = set()
    parent_ids = set()

    # Используем 0 как виртуальный ID для "Без категории"
    UNCATEGORIZED_ID = 0

    # 1. Собираем ID
    for transaction in transactions:
        cat_id = transaction["category_id"]
        if cat_id is None:
            all_category_ids.add(UNCATEGORIZED_ID)
        else:
            all_category_ids.add(cat_id)

        parent_id = transaction["category__parent_id"]
        if parent_id:
            parent_ids.add(parent_id)

    all_category_ids.update(parent_ids)

    # 2. Получаем инфу о реальных категориях из БД (исключая нашу виртуальную)
    real_ids = [cid for cid in all_category_ids if cid != UNCATEGORIZED_ID]
    categories_from_db = Category.objects.filter(id__in=real_ids).select_related(
        "parent"
    )
    category_db_info = {}

    for cat in categories_from_db:
        category_db_info[cat.id] = {
            "name": cat.name,
            "parent_id": cat.parent_id if cat.parent else None,
            "parent_name": cat.parent.name if cat.parent else None,
        }

    # 3. Инициализируем словарь категорий
    for cat_id in all_category_ids:
        if cat_id == UNCATEGORIZED_ID:
            categories[cat_id] = {
                "id": UNCATEGORIZED_ID,
                "name": "Без категории",
                "parent_id": None,
                "parent_name": None,
                "total_direct": 0,
                "total_with_children": 0,
                "children": [],
            }
        elif cat_id in category_db_info:
            info = category_db_info[cat_id]
            categories[cat_id] = {
                "id": cat_id,
                "name": info["name"],
                "parent_id": info["parent_id"],
                "parent_name": info["parent_name"],
                "total_direct": 0,
                "total_with_children": 0,
                "children": [],
            }
        else:
            # Заглушка, если категорию не нашли (теоретически невозможно при SET_NULL)
            categories[cat_id] = {
                "id": cat_id,
                "name": f"Category {cat_id}",
                "parent_id": None,
                "parent_name": None,
                "total_direct": 0,
                "total_with_children": 0,
                "children": [],
            }

    # 4. Считаем прямые суммы
    for transaction in transactions:
        cat_id = transaction["category_id"]
        if cat_id is None:
            cat_id = UNCATEGORIZED_ID

        if cat_id in categories:
            categories[cat_id]["total_direct"] += float(transaction["amount"] or 0)

    return categories


def link_children_to_parents(
    categories: Dict[int, Dict[str, Any]],
) -> Dict[int, Dict[str, Any]]:
    """
    Связывает дочерние категории с их родителями.
    """
    children_by_parent = defaultdict(list)

    for cat_id, cat_data in categories.items():
        parent_id = cat_data["parent_id"]
        if parent_id:
            children_by_parent[parent_id].append(cat_data)

    for parent_id, children in children_by_parent.items():
        if parent_id in categories:
            categories[parent_id]["children"] = children

    return categories


def calculate_hierarchical_totals(
    categories: Dict[int, Dict[str, Any]],
) -> Dict[int, Dict[str, Any]]:
    """
    Рекурсивно вычисляет суммы с учетом всех дочерних.
    """
    processed: Set[int] = set()

    def calculate_node_total(cat_id: int) -> float:
        if cat_id in processed:
            return categories[cat_id]["total_with_children"]

        cat_data = categories[cat_id]
        total = cat_data["total_direct"]

        for child in cat_data["children"]:
            total += calculate_node_total(child["id"])

        cat_data["total_with_children"] = total
        processed.add(cat_id)
        return total

    for cat_id, cat_data in categories.items():
        if cat_id not in processed:
            calculate_node_total(cat_id)

    return categories


def build_tree_from_roots(
    categories: Dict[int, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Строит дерево.
    """

    def build_subtree(parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        subtree = []

        for cat_data in categories.values():
            if cat_data["parent_id"] == parent_id:
                children = build_subtree(cat_data["id"])
                clean_category = create_clean_category(cat_data, children)
                subtree.append(clean_category)

        subtree.sort(key=lambda x: x["total"], reverse=True)
        return subtree

    return build_subtree()


def create_clean_category(
    category_data: Dict[str, Any], children: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Создает чистую структуру для сериализации.
    """
    clean_cat = {
        "id": category_data["id"],
        "name": category_data["name"],
        "total": category_data["total_with_children"],
        "total_direct": category_data["total_direct"],
        "children": children,
    }

    if category_data.get("parent_name"):
        clean_cat["parent"] = {
            "id": category_data["parent_id"],
            "name": category_data["parent_name"],
        }

    return clean_cat
