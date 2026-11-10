from django.urls import path

from accounts.views import (
    BalanceHistoryView,
    ListAccounts,
    RestoreAccountView,
    RetrieveUpdateDeleteAccount,
    ToggleAccountActiveStatusView,
)

urlpatterns = [
    path("", ListAccounts.as_view(), name="accounts"),
    path(
        "<int:pk>/",
        RetrieveUpdateDeleteAccount.as_view(),
        name="retrieve-update-delete-account",
    ),
    path(
        "<int:pk>/toggle-active/",
        ToggleAccountActiveStatusView.as_view(),
        name="toggle-account-active",
    ),
    path(
        "<int:pk>/restore/",
        RestoreAccountView.as_view(),
        name="restore-account",
    ),
    path(
        "balance-history/",
        BalanceHistoryView.as_view(),
        name="balance-history",
    ),
]
