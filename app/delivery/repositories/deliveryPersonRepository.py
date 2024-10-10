from datetime import timedelta
from app.delivery.models import DeliveryPerson
from django.db.models import Q


class DeliveryPersonRepository:
    def __init__(self):
        self = self

    def filter_persons_by_postalCode(self, postal_code):
        return DeliveryPerson.objects.filter(Q(available=True) & Q(postal_code_area=postal_code)).first()

    def filter_persons_by_postalCode_and_assignedTime(self, order, postal_code):
        return DeliveryPerson.objects.filter(Q(assigned_orders__lt=3) & Q(postal_code_area=postal_code) & Q(assigned_time__gt = order.order_time-timedelta(minutes=3))).first()

    def save(self, deliveryPerson):
        return deliveryPerson.save()