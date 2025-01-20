from django.urls import path

from .views import ListAccounts, RetrieveUpdateDeleteAccount

urlpatterns = [
    path("", ListAccounts.as_view(), name="accounts"),
    path(
        "<int:pk>/",
        RetrieveUpdateDeleteAccount.as_view(),
        name="retrieve-update-delete-account",
    ),
]
