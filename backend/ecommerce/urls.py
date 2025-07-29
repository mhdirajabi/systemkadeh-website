from django.contrib import admin
from django.urls import path
from .views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", health_check),
]
