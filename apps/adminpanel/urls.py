from django.urls import path
from . import views


app_name = 'adminpanel'

urlpatterns = [
    path('', views.PanelDashboardView.as_view(), name='dashboard'),
]
