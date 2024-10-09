from django.urls import path
from app.orders import views

urlpatterns = [
    path('validate_discount_code/', views.validate_discount_code, name='validate_discount_code'),
    path('order/', views.create_order, name='create_order'),
]
