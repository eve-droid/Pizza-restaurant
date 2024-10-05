from . import views
from django.urls import path

urlpatterns = [
    path('calculate_earnings/', views.generate_earning_report, name='calculate_earnings'),
    path('monitoring/', views.monitoring, name='monitoring'),
]