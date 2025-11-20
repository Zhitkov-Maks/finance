from django.urls import path

from .views import GetAnalyticForMonth

urlpatterns = [
    path("month/", GetAnalyticForMonth.as_view(), name="analytics"),
]
