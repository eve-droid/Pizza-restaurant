from django.urls import path
from . import views

urlpatterns = [
    path('validate_discount_code/', views.validate_discount_code, name='validate_discount_code'),
    path('order/', views.create_order, name='create_order'),
    path('order/success/<int:pk>/', views.order_success, name='order_success'),
    path('order/<int:order_id>/track/', views.track_order, name='track_order'),
    path('order/<int:order_id>/start_delivery/', views.start_delivery, name='start_delivery'),
    path('order/<int:order_id>/mark_as_delivered/', views.mark_as_delivered, name='mark_as_delivered'),
]
