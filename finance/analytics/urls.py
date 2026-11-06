from django.urls import path

from .views import ForecastView, GetAnalyticForMonth

urlpatterns = [
    path("month/", GetAnalyticForMonth.as_view(), name="analytics"),
    path("forecast/", ForecastView.as_view(), name="forecast"),
]
