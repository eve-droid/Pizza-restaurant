from datetime import datetime, timedelta
from django.db import models

from app.customers.models import Customer
from app.discounts.models import Discount

class Pizza(models.Model):
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
    pizzas = models.ManyToManyField(Pizza)
    desserts = models.ManyToManyField(Dessert, blank=True)
    drinks = models.ManyToManyField(Drink, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
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

        #offer a free pizza and drind if it's customer's birthday
        if self.customer.birthday == datetime.now().date():
            if self.pizzas.exists():
                self.price -= min(pizza.price for pizza in self.pizzas.all())
            if self.drinks.exists():
                self.price -= min(drink.price for drink in self.drinks.all())

        # Apply 10% discount if the customer is eligible
        if self.customer.is_eligible_for_discount():
            self.price = self.price * 0.9
            self.customer.count_pizza %= 10 # Reset the count of pizzas

        return self.price

    def apply_discount(self, discount_code):
        if discount_code != '':
            try:
                discount = Discount.objects.get(discount_code=discount_code)
                if discount.is_valid() and not self.has_discount_code:
                    self.price = self.price * (1 - discount.discount/100)
                    discount.used = True
                    self.has_discount_code = True
                    discount.save()
                elif self.has_discount_code:
                    raise ValueError('A dicount code has already been applied')
            except ValueError as e:
                raise ValueError('Invalid discount code')
    
        return self.price
    
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
    


class Delivery(models.Model):
    Delivery_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='deliveries', null=False)
    delivery_time = models.DateTimeField(null=True, blank=True)

    def set_delivery_time(self):
        #Set the delivery time when the delivery starts.
        if not self.delivery_time:
            self.delivery_time = datetime.now() + timedelta(minutes=30)
            self.save()
