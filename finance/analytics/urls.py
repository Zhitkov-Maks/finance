from django.urls import path

from .views import ForecastView, GetAnalyticForDay, GetAnalyticForMonth

urlpatterns = [
    path("month/", GetAnalyticForMonth.as_view(), name="analytics"),
    path("forecast/", ForecastView.as_view(), name="forecast"),
    path('day/', GetAnalyticForDay.as_view(), name='analytics-day'),
]
