from django.urls import path

from .views import (
    TransferAnalyticsView,
    TransferDetailView,
    TransferFundsView,
    TransferHistoryView,
)

urlpatterns = [
    path("", TransferFundsView.as_view(), name="transfer_funds"),
    path("history/", TransferHistoryView.as_view(), name="transfer_history"),
    path(
        "analytics/",
        TransferAnalyticsView.as_view(),
        name="transfer-analytics",
    ),
    path("<int:pk>/", TransferDetailView.as_view(), name="transfer_detail"),
]
