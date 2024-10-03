from datetime import datetime, timedelta
from decimal import ROUND_UP, Decimal
from django.db import models

from app.customers.models import Customer
from app.discounts.models import Discount

class Pizza(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.name
    
    def calculate_price(self):
        # Calculate the price of the pizza based on the ingredients
        self.price = Decimal(0.2) #price of the flour for the pizza base
        for ingredient in self.get_ingredients():
            self.price += All_Ingredients.objects.get(name = ingredient).price

        self.price += (self.price* Decimal(0.4))
        self.price += (self.price* Decimal(0.09))
        self.price = self.price.quantize(Decimal('1'), rounding=ROUND_UP) - Decimal(0.01)
        self.price = self.price.quantize(Decimal('0.01'), rounding=ROUND_UP)
        return self.price
    
    def get_ingredients(self):
        # Get the ingredients of the pizza
        return self.ingredients.split(', ')

    
    
class All_Ingredients(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

class Dessert(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

class Drink(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

    
class Order(models.Model):
    Status_Choices = [
        ('Processing', 'Processing'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    order_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=Status_Choices, default='Processing')
    delivery = models.OneToOneField('Delivery', null=True, blank=True, on_delete=models.SET_NULL)
    has_discount_code = models.BooleanField(default=False)


    def get_total_price(self):
        # Calculate the total price of the order
        self.price = 0

        pizzas = [item for item in self.items.filter(pizza__isnull=False)]
        desserts = [item for item in self.items.filter(dessert__isnull=False)]
        drinks = [item for item in self.items.filter(drink__isnull=False)]

        for pizza in pizzas:
            self.price += pizza.pizza.calculate_price() * pizza.quantity
        for dessert in desserts:
            self.price += dessert.dessert.price * dessert.quantity
        for drink in drinks:
            self.price += drink.drink.price * drink.quantity

        return self.price

    def apply_discount(self, discount_code, discount_error=False):
        if discount_code != '':
            try:
                discount = Discount.objects.get(discount_code=discount_code)
                if discount.is_valid() and not self.has_discount_code:
                    self.price = self.price * Decimal(1 - discount.percentage/100)
                    discount.used = True
                    self.has_discount_code = True
                    discount.save()
                elif self.has_discount_code:
                    discount_error = 'A dicount code has already been applied'
            except ValueError as e:
                discount_error = 'Invalid discount code'
    
        return self.price, discount_error
    
    def estimate_delivery_time(self):
        #Estimate the delivery time to be 30 minutes after the order time.
        return self.order_time + timedelta(minutes=30)

    def update_status(self, new_status):
        #Update the status of the order.
        self.status = new_status
        self.save()



    def cancel_order(self):
        if self.status == 'Delivered':
            raise ValueError('Cannot cancel delivered order')
        elif self.status == 'Cancelled':
            raise ValueError('Order is already cancelled')
        elif self.order_time + timedelta(minutes=5) < datetime.now():
            raise ValueError('Cannot cancel order after 5 minutes')
        else:
            self.delete()
    

class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name = 'items', on_delete=models.CASCADE)
    pizza = models.ForeignKey('Pizza',null = True, blank = True, on_delete=models.CASCADE)
    drink = models.ForeignKey('Drink',null = True, blank = True, on_delete=models.CASCADE)
    dessert = models.ForeignKey('Dessert',null = True, blank = True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Quantity of each pizza

    def __str__(self):
        return f"{self.quantity} x {self.pizza.name} for Order #{self.order.id}"

class Delivery(models.Model):
    Delivery_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='deliveries', null=False)
    delivery_time = models.DateTimeField(null=True, blank=True)

    def set_delivery_time(self):
        #Set the delivery time when the delivery starts.
        if not self.delivery_time:
            self.delivery_time = datetime.now() + timedelta(minutes=30)
