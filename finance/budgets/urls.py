from django.urls import path

from .views import (
    BudgetDetailView,
    BudgetListCreateView,
    BudgetSummaryView,
)

app_name = "budgets"

urlpatterns = [
    path("", BudgetListCreateView.as_view(), name="list-create"),
    path("summary/", BudgetSummaryView.as_view(), name="summary"),
    path("<int:pk>/", BudgetDetailView.as_view(), name="detail"),
]
