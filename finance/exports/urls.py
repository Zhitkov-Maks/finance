from django.urls import path

from .views import ExportView

urlpatterns = [
    path("", ExportView.as_view(), name="data-export"),
]
