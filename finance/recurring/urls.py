from django.urls import path

from .views import RecurringDetailView, RecurringListCreateView, UpcomingPaymentsView

urlpatterns = [
    path("", RecurringListCreateView.as_view(), name="list-create"),
    path("<int:pk>/", RecurringDetailView.as_view(), name="detail"),
    path("upcoming/", UpcomingPaymentsView.as_view(), name="upcoming"),
]
