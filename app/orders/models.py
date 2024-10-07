from datetime import datetime, timedelta
from decimal import ROUND_UP, Decimal
from django.db import models
from django.utils import timezone


from app.customers.models import Customer
from app.discounts.models import Discount

class Pizza(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.CharField(max_length=200, default='')
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def calculate_price(self):
        #calculate price of a pizza based on the ingredients
        self.price = Decimal(0.2) #price of flour for the pizza base
        for ingredient in self.get_ingredients():
            self.price += All_Ingredients.objects.get(name = ingredient).price

        self.price += (self.price* Decimal(0.4))
        self.price += (self.price* Decimal(0.09))
        self.price = self.price.quantize(Decimal('1'), rounding=ROUND_UP) - Decimal(0.01)
        self.price = self.price.quantize(Decimal('0.01'), rounding=ROUND_UP)
        return self.price
    
    def check_if_vegetarian(self):
        # Check if the pizza is vegetarian
        for ingredient in self.get_ingredients():
            if ingredient.vegetarian == False:
                return False
        return True
    
    def get_ingredients(self):
        return self.ingredients.split(', ')

    
    
class All_Ingredients(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    vegetarian = models.BooleanField(default=False)

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
        ('Your order is being prepared', 'Your order is being prepared'),  # Added new status for Making
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    order_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=Status_Choices, default='Processing')
    delivery = models.OneToOneField('Delivery', null=True, blank=True, on_delete=models.SET_NULL)
    delivery_person = models.ForeignKey('DeliveryPerson', on_delete=models.SET_NULL, null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    has_discount_code = models.BooleanField(default=False)

    def get_total_price(self):
        # calculate total price of the order
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
                    self.price = self.price * Decimal(1 - discount.percentage / 100)
                    discount.used = True
                    self.has_discount_code = True
                    discount.save()
                elif self.has_discount_code:
                    discount_error = 'A discount code has already been applied'
            except ValueError as e:
                discount_error = 'Invalid discount code'

        return self.price, discount_error

    def estimate_delivery_time(self):
        # estimate the delivery time to be 30 minutes after the order time.
        return self.order_time + timedelta(minutes=30)

    def auto_update_status(self):
        """
        Automatically update the status of the order based on elapsed time and delivery progress.
        """
        now = timezone.now()
        time_since_order = now - self.order_time

        # Step 1: After 5 minutes, change from "Processing" to "Making"
        if self.status == 'Processing' and time_since_order > timedelta(minutes=5):
            self.status = 'Your order is being prepared'
            self.save()

        # Step 2: After 15 minutes (total 20 mins), change from "Making" to "Out for Delivery"
        if self.status == 'Your order is being prepared' and time_since_order > timedelta(minutes=20):
            self.status = 'Out for Delivery'
            self.estimated_delivery_time = now + timedelta(minutes=30)  # Update estimated delivery time
            self.save()

        # Step 3: Change to "Delivered" once the estimated delivery time is reached
        if self.status == 'Out for Delivery' and now >= self.estimated_delivery_time:
            self.status = 'Delivered'
            self.save()

    def update_status(self, new_status):
        # update the status of the order.
        self.status = new_status
        self.save()

    def cancel_order(self):
        for item in self.items.all():
            if item.pizza:
                self.customer.count_pizza -= item.quantity
        self.customer.save()
        self.status = 'Cancelled'
        return self

    

class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name = 'items', on_delete=models.CASCADE)
    pizza = models.ForeignKey('Pizza',null = True, blank = True, on_delete=models.CASCADE)
    drink = models.ForeignKey('Drink',null = True, blank = True, on_delete=models.CASCADE)
    dessert = models.ForeignKey('Dessert',null = True, blank = True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # pizza quantity

    def __str__(self):
        return f"{self.quantity} x {self.pizza.name} for Order #{self.order.id}"

class Delivery(models.Model):
    Delivery_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='deliveries', null=False)
    delivery_time = models.DateTimeField(null=True, blank=True)

    def set_delivery_time(self):
        #time for when the delivery starts
        if not self.delivery_time:
            self.delivery_time = datetime.now() + timedelta(minutes=30)

class DeliveryPerson(models.Model):
    name = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20) #postal code area they are assigned to
    available = models.BooleanField(default=True) #true if they are available for delivery
    assigned_orders = models.IntegerField(default=0) #number of orders they are handling
    
    def __str__(self):
        return f"{self.name} - {self.postal_code}"
    
    def is_available(self):
        return self.available and self.assigned_orders < 3
    
    def assign_delivery_person(self):
        available_person = DeliveryPerson.objects.filter(available=True).first()
        if available_person:
            self.delivery_person = available_person
            available_person.assigned_orders += 1
            available_person.save()
            self.save()


def calculate_estimated_delivery_time(self):
    if self.delivery_person:
        minutes_per_order = 30
        additional_minutes = self.delivery_person.assigned_orders * minutes_per_order
        estimated_time = datetime.now() + timedelta(minutes=additional_minutes)
        self.estimated_delivery_time = estimated_time
        self.save()
        print(f"Estimated Delivery Time: {estimated_time}")  # Debugging log
    else:
        print("No delivery person assigned!")  # Debugging log