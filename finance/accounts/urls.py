from django.urls import path

from .views.views_account import (
    ListAccounts,
    RetrieveUpdateDeleteAccount,
    ToggleAccountActiveStatusView,
)
from .views.views_debt import (
    CreateDebtAccountsView,
    CreateDebtView,
    RepayDebtView,
    DebtListView,
    DebtDetailView
)
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
    path(
        "transfers/history/",
        TransferHistoryView.as_view(),
        name="transfer_history"
    ),
    path(
        "transfer/<int:pk>/",
        TransferDetailView.as_view(),
        name="transfer_detail"
    ),
    path(
        "<int:pk>/toggle-active/",
        ToggleAccountActiveStatusView.as_view(),
        name="toggle-account-active",
    ),
    path(
        'debts/create-debt-accounts/',
        CreateDebtAccountsView.as_view(),
        name='create_debt_accounts'),
    path(
        'debts/create-debt/',
        CreateDebtView.as_view(),
        name='create_debt'
    ),
    path(
        'debts/repay-debt/',
        RepayDebtView.as_view(),
        name='repay_debt'
    ),
    path('debts/', DebtListView.as_view(), name='debts'),
    path(
        'debts/<int:debt_id>/',
        DebtDetailView.as_view(),
        name='debt_detail'
    ),
]
