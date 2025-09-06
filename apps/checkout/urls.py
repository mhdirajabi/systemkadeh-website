from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.CheckoutView.as_view(), name='checkout'),
    path('success/<str:order_number>/', views.CheckoutSuccessView.as_view(), name='checkout_success'),
    path('cancel/', views.CheckoutCancelView.as_view(), name='checkout_cancel'),
]