from django.db import transaction
from app.orders.repositories.orderItemRepository import OrderItemRepository
from app.orders.repositories.orderRepository import OrderRepository

class UnitOfWork:
    def __init__(self):
        self.orders = OrderRepository()  # Order repository
        self.order_items = OrderItemRepository()  # OrderItem repository
        self._committed = False

    def commit(self):
        #Start an atomic transaction 
        with transaction.atomic():
            self.orders.save_order()  # Save the orders
            self.order_items.save_order_item()  #Save the order items
        self._committed = True

    
