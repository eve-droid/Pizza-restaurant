from app.management import monitoringViews
from . import earningViews
from django.urls import path

urlpatterns = [
    path('calculate_earnings/', earningViews.generate_earning_report, name='calculate_earnings'),
    path('monitoring/', monitoringViews.monitoring, name='monitoring'),
]