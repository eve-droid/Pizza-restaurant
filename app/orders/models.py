from datetime import datetime, timedelta
from django.db import models

from app.customers.models import Customer

class Pizza(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

class Dessert(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

class Drink(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    
class Order(models.Model):
    Status_Choices = [
        ('Processing', 'Processing'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    pizzas = models.ManyToManyField(Pizza)
    desserts = models.ManyToManyField(Dessert, blank=True)
    drinks = models.ManyToManyField(Drink, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    order_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=Status_Choices, default='Processing')
    delivery = models.OneToOneField('Delivery', null=True, blank=True, on_delete=models.SET_NULL)
    def get_total_price(self):
        # Calculate the total price of the order
        self.price = 0
        for pizza in self.pizzas.all():
            self.price += pizza.price
        for dessert in self.desserts.all():
            self.price += dessert.price
        for drink in self.drinks.all():
            self.price += drink.price
        return self.price
    
    def estimate_delivery_time(self):
        #Estimate the delivery time to be 30 minutes after the order time.
        return self.order_time + timedelta(minutes=30)

    def update_status(self, new_status):
        #Update the status of the order.
        self.status = new_status
        self.save()

    #def apply_discount(self):
        ## Apply 10% discount if the customer is eligible
        #if self.cu
        #elif self.customer.is_eligible_for_discount():
        #    self.price = self.price * 0.9
        #    self.customer.count_pizza = 0 # Reset the count of pizzas

    def cancel_order(self):
        if self.status == 'Delivered':
            raise ValueError('Cannot cancel delivered order')
        elif self.status == 'Cancelled':
            raise ValueError('Order is already cancelled')
        elif self.order_time + timedelta(minutes=5) < datetime.now():
            raise ValueError('Cannot cancel order after 5 minutes')
        else:
            self.status = 'Cancelled'
    


class Delivery(models.Model):
    Delivery_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='deliveries')
    delivery_time = models.DateTimeField(null=True, blank=True)

    def set_delivery_time(self):
        #Set the delivery time when the delivery starts.
        if not self.delivery_time:
            self.delivery_time = datetime.now() + timedelta(minutes=30)
            self.save()
