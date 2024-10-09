from django.urls import path
from . import views

urlpatterns = [
    path('order/success/<int:pk>/', views.order_success, name='order_success'),
]