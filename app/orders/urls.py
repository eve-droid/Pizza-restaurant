from django.urls import path
from . import views

urlpatterns = [
    path('order/', views.create_order, name='create_order'),
    path('order/success/', views.order_success, name='order_success'),
]
