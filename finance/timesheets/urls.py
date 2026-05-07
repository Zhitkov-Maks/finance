from django.urls import path


from .views import GetTimesheetsSettings, GetShifts, GetShiftsForDay, \
    ManyAddShifts, StatisticForMonth, StatisticForYear

urlpatterns = [
    path("settings/", GetTimesheetsSettings.as_view(), name="get_settings"),
    path("shifts/", GetShifts.as_view(), name="shifts"),
    path("shifts/<str:day_id>/", GetShiftsForDay.as_view(), name="shifts_day_id"),
    path("add-many-shifts/", ManyAddShifts.as_view(), name="many_add"),
    path("statistics/year/", StatisticForYear.as_view(), name="stat_year"),
    path("statistics/month/", StatisticForMonth.as_view(), name="stat_month")
]
