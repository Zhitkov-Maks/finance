from django.urls import path

from .views import (
    IncomeView,
    RetrieveUpdateDeleteIncome,
    ListCategory,
    RetrieveUpdateDeleteCategory,
)

urlpatterns = [
    path("incomes/", IncomeView.as_view(), name="incomes"),
    path(
        "incomes/<int:pk>/",
        RetrieveUpdateDeleteIncome.as_view(),
        name="retrieve-update-delete-income",
    ),
    path("incomes/category/", ListCategory.as_view(), name="category"),
    path(
        "incomes/category/<int:pk>/",
        RetrieveUpdateDeleteCategory.as_view(),
        name="retrieve-update-delete-category",
    ),
]
