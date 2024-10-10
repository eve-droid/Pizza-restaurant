from app.orders.models import Order, OrderItem


class OrderItemRepository:
    def __init__(self):
        self._order_items = [] #empty list for dirty order items

    def create_order_item(self, order, quantity, pizza=None, drink=None, dessert=None):
        order_item = OrderItem(order=order, pizza=pizza, drink=drink, dessert=dessert, quantity=quantity)
        self.add(order_item)
        return order_item

    def add(self, order_item):
        self._order_items.append(order_item)

    def save_order_item(self):
        for dirty_order_item in self._order_items:
            dirty_order_item.save()
        self._order_items.clear()

    def get_order_items(self, order):
        return order.items.all()
    
    def get_pizzas(self, order):
        return order.items.filter(pizza__isnull=False)
    
    def get_drinks(self, order):
        return order.items.filter(drink__isnull=False)
    
    def get_desserts(self, order):
        return order.items.filter(dessert__isnull=False)