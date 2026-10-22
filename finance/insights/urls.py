from django.urls import path

from .views import InsightDismissView, InsightListView

app_name = "insights"

urlpatterns = [
    path("", InsightListView.as_view(), name="list"),
    path("<uuid:pk>/dismiss/", InsightDismissView.as_view(), name="dismiss"),
]
