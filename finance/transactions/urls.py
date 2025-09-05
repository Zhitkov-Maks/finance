from django.urls import path

from .views import (
    TransactionView,
    RetrieveUpdateDeleteTransaction,
    ListCategory,
    RetrieveUpdateDeleteCategory,
    CategoryTransactionStatisticsView,
)

urlpatterns = [
    path("", TransactionView.as_view(), name="incomes"),
    path(
        "<int:pk>/",
        RetrieveUpdateDeleteTransaction.as_view(),
        name="retrieve-update-delete-income",
    ),
    path("category/", ListCategory.as_view(), name="category"),
    path(
        "category/<int:pk>/",
        RetrieveUpdateDeleteCategory.as_view(),
        name="retrieve-update-delete-category",
    ),
    path(
        "statistics/",
        CategoryTransactionStatisticsView.as_view(),
        name="statistics"
    ),
]
