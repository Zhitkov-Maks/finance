from django.urls import path

from .views.views_account import ListAccounts, RetrieveUpdateDeleteAccount
from .views.views_transfer import (
    TransferFundsView,
    TransferHistoryView,
    TransferDetailView,
)

urlpatterns = [
    path("", ListAccounts.as_view(), name="accounts"),
    path(
        "<int:pk>/",
        RetrieveUpdateDeleteAccount.as_view(),
        name="retrieve-update-delete-account",
    ),
    path("transfer/", TransferFundsView.as_view(), name="transfer_funds"),
    path("transfers/history/", TransferHistoryView.as_view(), name="transfer_history"),
    path("transfer/<int:pk>/", TransferDetailView.as_view(), name="transfer_detail"),
]
