from app.delivery.models import Delivery


class DeliveryRepository:
    def __init__(self):
        self = self

    def get_delivery_by_order(self, order):
        return Delivery.objects.get(order=order)
    
    def get_delivery_by_order_id(self, order_id):
        return Delivery.objects.get(id=order_id)
    
    def create_delivery(self, order):
        delivery = Delivery(order=order)
        delivery.save()
        return delivery
    
    def save(self, delivery):   
        delivery.save()

    