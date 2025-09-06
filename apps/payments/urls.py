from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('verify/<uuid:payment_id>/', views.verify_payment, name='verify_payment'),
    path('callback/<uuid:payment_id>/', views.payment_callback, name='payment_callback'),
    path('refund/<uuid:payment_id>/', views.refund_payment, name='refund_payment'),
]