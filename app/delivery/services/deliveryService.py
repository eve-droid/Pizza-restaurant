from datetime import timedelta, timezone
from django.utils import timezone
from app.delivery.repositories.deliveryRepository import DeliveryRepository


class DeliveryService:
    def __init__(self):
        self.deliveryRepository = DeliveryRepository()
        

    def get_delivery_by_order(self, order):
        return self.deliveryRepository.get_delivery_by_order(order)
    
    def get_delivery_by_order_id(self, order_id):
        return self.deliveryRepository.get_delivery_by_order_id(order_id)
    
    def create_delivery(self, order):
        return self.deliveryRepository.create_delivery(order)
    
    
    def set_delivery_time(self, delivery):
        # Set the estimated delivery time for the order
        delivery.estimated_delivery_time = timezone.now() + timedelta(minutes=30)
        self.deliveryRepository.save(delivery)


    def save(self, delivery):
        return self.deliveryRepository.save(delivery)
    
