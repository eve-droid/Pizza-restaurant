from app.orders.models import Order
from django.db.models.functions import ExtractMonth


class OrderRepository:
    def __init__(self):
        self._orders = [] #empty list for dirty orders

    def get_order_by_id(self, order_id):
        return Order.objects.get(id=order_id)

    def get_all_orders(self):
        return Order.objects.all()
    
    def add(self, order):
        self._orders.append(order) #add order to dirty list
    
    def save_order(self):
        for dirty_order in self._orders:
            dirty_order.save()
        self._orders.clear()

    def update_order(self, order):
        order.save()
        return order
    
    def filter_orders_by_status(self, status, orders):
        return orders.filter(status__in=status)
    
    def filter_orders_by_region(self, region, orders):
        return orders.filter(customer__region=region)
    
    def filter_orders_by_month(self, month, orders):
        return orders.annotate(month=ExtractMonth('order_time')).filter(month = month)
    
    def filter_orders_by_gender(self, gender, orders):
        return orders.filter(customer__gender = gender)
    
    def filter_orders_by_customer_age(self, earliestBirthday, latestBirthday, orders):
        return orders.filter(customer__birthday__range = (earliestBirthday, latestBirthday))
    

    


        

