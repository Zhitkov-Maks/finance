from django.urls import path


from .views import (
    TransferFundsView,
    TransferHistoryView,
    TransferDetailView,
)

urlpatterns = [

    path("", TransferFundsView.as_view(), name="transfer_funds"),
    path(
        "history/",
        TransferHistoryView.as_view(),
        name="transfer_history"
    ),
    path(
        "<int:pk>/",
        TransferDetailView.as_view(),
        name="transfer_detail"
    ),
]
