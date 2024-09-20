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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    pizzas = models.ManyToManyField(Pizza)
    desserts = models.ManyToManyField(Dessert, blank=True)
    drinks = models.ManyToManyField(Drink, blank=True)
    price = models.IntegerField()
    order_time = models.DateTimeField()
    status = models.CharField(max_length=100)

    def get_total_price(self):
        # Calculate the total price of the order
        self.price = 0
        for pizza in self.pizzas.all():
            self.price += pizza.price
        for dessert in self.desserts.all():
            self.price += dessert.price
        for drink in self.drinks.all():
            self.price += drink.price

    def apply_discount(self):
        # Apply 10% discount if the customer is eligible
        if self.cu
        elif self.customer.is_eligible_for_discount():
            self.price = self.price * 0.9
            self.customer.count_pizza = 0 # Reset the count of pizzas

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
    delivery_id = models.IntegerField(primary_key=True)
    order_id = models.IntegerField()
    delivery_time = models.DateTimeField()

