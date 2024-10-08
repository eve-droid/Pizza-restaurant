from django.urls import path
from app.orders.views import orderSuccessViews, orderViews

urlpatterns = [
    path('validate_discount_code/', orderViews.validate_discount_code, name='validate_discount_code'),
    path('order/', orderViews.create_order, name='create_order'),
    path('order/success/<int:pk>/', orderSuccessViews.order_success, name='order_success'),
    path('order/success/<int:pk>/<str:status>/', orderSuccessViews.update_status, name='update_status'),
    path('order/success/<int:pk>/', orderSuccessViews.cancel_order, name='cancel_order'),
]
