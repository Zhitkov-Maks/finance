"""
URL configuration for finance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from .views import health_check

# Версия api
v = "v1"

urlpatterns = [
    path('health/', health_check, name='health'),
    path("admin/", admin.site.urls),
    path("api/vi/dfr_auth/", include("rest_framework.urls")),
    path(f"api/{v}/auth/", include("djoser.urls")),
    re_path("auth/", include("djoser.urls.authtoken")),
    path(f"api/{v}/accounts/", include("accounts.urls")),
    path(f"api/{v}/transaction/", include("transactions.urls")),
    path(f'api/{v}/analitycs/', include('analytics.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path(f"api/{v}/transfer/", include('transfer.urls')),
    path(f'api/{v}/debts/', include('debt.urls')),
    path(f'api/{v}/timesheets/', include('timesheets.urls'))
]
