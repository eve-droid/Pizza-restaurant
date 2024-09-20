from datetime import datetime, timedelta
from django.db import models

from app.customers.models import Customer
from app.discounts.models import Discount

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
    has_discount_code = models.BooleanField(default=False)

    def get_total_price(self):
        # Calculate the total price of the order
        self.price = 0
        for pizza in self.pizzas.all():
            self.price += pizza.price
        for dessert in self.desserts.all():
            self.price += dessert.price
        for drink in self.drinks.all():
            self.price += drink.price

        # Apply 10% discount if the customer is eligible
        if self.customer.is_eligible_for_discount():
            self.price = self.price * 0.9
            self.customer.count_pizza %= 10 # Reset the count of pizzas

    def apply_discount(self, discount_code):
        try:
            discount = Discount.objects.get(discount_code=discount_code)
            if discount.is_not_expired() and not self.has_discount_code:
                self.price = self.price * (1 - discount.discount/100)
                discount.used = True
                self.has_discount_code = True
                discount.save()
            elif self.has_discount_code:
                raise ValueError('A dicount code has already been applied')
            elif not discount.is_not_expired():
                raise ValueError('Discount code has expired')
        except Discount.DoesNotExist:
            raise ValueError('Invalid discount code')
        

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

