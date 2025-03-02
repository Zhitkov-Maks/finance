from django.urls import path

from .views import (
    ExpenseView,
    RetrieveUpdateDeleteExpense,
    ListCategoryExpense,
    RetrieveUpdateDeleteCategoryExpense,
    CategoryExpenseStatisticsView,
)

urlpatterns = [
    path("", ExpenseView.as_view(), name="incomes"),
    path(
        "<int:pk>/",
        RetrieveUpdateDeleteExpense.as_view(),
        name="retrieve-update-delete-expense",
    ),
    path("category/", ListCategoryExpense.as_view(), name="category"),
    path(
        "category/<int:pk>/",
        RetrieveUpdateDeleteCategoryExpense.as_view(),
        name="retrieve-update-delete-category-expense",
    ),
    path(
        "statistics/",
        CategoryExpenseStatisticsView.as_view(),
        name="statistics"
    ),
]
