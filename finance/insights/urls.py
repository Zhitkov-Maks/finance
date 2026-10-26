from django.urls import path

from .gamification_views import GamificationDashboardView
from .views import (
    GoalCurrentView,
    InsightDismissView,
    InsightListView,
    InsightSettingsView,
)

app_name = "insights"

urlpatterns = [
    path("", InsightListView.as_view(), name="list"),
    path("<uuid:pk>/dismiss/", InsightDismissView.as_view(), name="dismiss"),
    path("gamification/", GamificationDashboardView.as_view(), name="gamification"),
    path("goals/current/", GoalCurrentView.as_view(), name="goal-current"),
    path("settings/", InsightSettingsView.as_view(), name="settings"),
]
