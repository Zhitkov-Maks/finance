from django.urls import path

from .views import (
    IncomeView,
    RetrieveUpdateDeleteIncome,
    ListCategory,
    RetrieveUpdateDeleteCategory,
    CategoryIncomeStatisticsView,
)

urlpatterns = [
    path("", IncomeView.as_view(), name="incomes"),
    path(
        "<int:pk>/",
        RetrieveUpdateDeleteIncome.as_view(),
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
        CategoryIncomeStatisticsView.as_view(),
        name="statistics"
    ),
]
