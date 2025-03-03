from django.urls import path

from accounts.views import (
    ListAccounts,
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
]
