from datetime import datetime, timedelta
from decimal import ROUND_UP, Decimal
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save
from django.db.models import Q



from app.customers.models import Customer
from app.discounts.models import Discount

class Pizza(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.CharField(max_length=200, default='')
    is_vegetarian = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def calculate_price(self):
        # Calculate price of a pizza based on the ingredients
        self.price = Decimal(0.2)  # Price of flour for the pizza base
        for ingredient in self.get_ingredients():
            self.price += All_Ingredients.objects.get(name=ingredient).price

        self.price += (self.price * Decimal(0.4))
        self.price += (self.price * Decimal(0.09))
        self.price = self.price.quantize(Decimal('1'), rounding=ROUND_UP) - Decimal(0.01)
        self.price = self.price.quantize(Decimal('0.01'), rounding=ROUND_UP)
        return self.price
    
    def check_if_vegetarian(self):
        # Check if the pizza is vegetarian
        for ingredient in self.get_ingredients():
            if All_Ingredients.objects.get(name=ingredient).vegetarian == False:
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
        ('Your Order is being prepared', 'Your Order is being prepared'),  # Added new status for Your Order is being prepared
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    order_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=Status_Choices, default='Processing')
    has_discount_code = models.BooleanField(default=False)

    def get_total_price(self):
        # Calculate total price of the order
        self.price = 0

        pizzas = self.items.filter(pizza__isnull=False)
        desserts = self.items.filter(dessert__isnull=False)
        drinks = self.items.filter(drink__isnull=False)

        for pizza in pizzas:
            self.price += pizza.pizza.calculate_price() * pizza.quantity
        for dessert in desserts:
            self.price += dessert.dessert.price * dessert.quantity
        for drink in drinks:
            self.price += drink.drink.price * drink.quantity

        return self.price

    def apply_discount(self, discount_code, discount_error=False):
        if discount_code:
            try:
                discount = Discount.objects.get(discount_code=discount_code)
                if discount.is_valid() and not self.has_discount_code:
                    self.price *= Decimal(1 - discount.percentage / 100)
                    discount.used = True
                    self.has_discount_code = True
                    discount.save()
                elif self.has_discount_code:
                    discount_error = 'A discount code has already been applied.'
            except Discount.DoesNotExist:
                discount_error = 'This discount code is not valid.'

        return self.price, discount_error


    def auto_update_order_status(self):
        now = timezone.now()
        time_since_order = now - self.order_time
        delivery = Delivery.objects.get(order=self)
        print(time_since_order)

        # Step 1: After 5 minutes, change from "Processing" to "Your Order is being prepared"
        if self.status == 'Processing' and time_since_order > timedelta(minutes=5):
            self.status = 'Your Order is being prepared'
            print(self.status)

        # Step 2: After 15 minutes (total 20 mins), change from "Your Order is being prepared" to "Out for Delivery"
        elif self.status == 'Your Order is being prepared' and time_since_order > timedelta(minutes=20):
            self.status = 'Out for Delivery'
            self.estimated_delivery_time = now + timedelta(minutes=30)  # Update estimated delivery time

        # Step 3: Change to "Delivered" once the estimated delivery time is reached
        elif self.status == 'Out for Delivery' and now >= delivery.estimated_delivery_time:
            delivery.deliver_order()  # Call the method to handle order delivery
            self.status = 'Delivered'

        self.save()

    def cancel_order(self):
        print("Cancelling order")
        for item in self.items.all():
            if item.pizza:
                self.customer.count_pizza -= item.quantity
        self.customer.save()
        self.status = 'Cancelled'
        delivery = Delivery.objects.get(order=self)
        delivery_person = delivery.delivery_person
        delivery_person.delivery_done()
        self.save()
        return self


class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name='items', on_delete=models.CASCADE)
    pizza = models.ForeignKey('Pizza', null=True, blank=True, on_delete=models.CASCADE)
    drink = models.ForeignKey('Drink', null=True, blank=True, on_delete=models.CASCADE)
    dessert = models.ForeignKey('Dessert', null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Pizza quantity

    def __str__(self):
        return f"{self.quantity} x {self.pizza.name} for Order #{self.order.id}"


class Delivery(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    delivery_person = models.ForeignKey('DeliveryPerson', on_delete=models.SET_NULL, null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)

    def assign_delivery_person(self, order):
        postal_code = order.customer.address_postal_code
        
        #if there is someone with the right postal code, which already has been assigned with max 2 deliveries in the last 3 min, select that delivery person
        delivery_person = DeliveryPerson.objects.filter(Q(assigned_orders__lt=3) & Q(postal_code_area=postal_code) & Q(assigned_time__gt = order.order_time-timedelta(minutes=3))).first()
        if delivery_person:
            delivery_person.set_delivery_person()
            self.delivery_person = delivery_person
        else:
            #else select someone who is available and has the correct postal code
            delivery_person = DeliveryPerson.objects.filter(Q(available=True) & Q(postal_code_area=postal_code)).first()
            if delivery_person:
                delivery_person.set_delivery_person()
                self.delivery_person = delivery_person
            else:
                #else select someone who is available and has no postal code assigned
                delivery_person = DeliveryPerson.objects.filter(postal_code_area = None).first() #assumption, we will always have enough personal for this case
                delivery_person.postal_code_area = postal_code
                delivery_person.set_delivery_person()
                self.delivery_person = delivery_person
        
        self.save()

    def set_delivery_time(self):
        # Set the estimated delivery time for the order
        self.estimated_delivery_time = timezone.now() + timedelta(minutes=30)
        self.save()

    def deliver_order(self):
        delivery_person = self.delivery_person
        if delivery_person:
            delivery_person.delivery_done()
        




class DeliveryPerson(models.Model):
    name = models.CharField(max_length=100)
    postal_code_area = models.CharField(max_length=100, null = True, default=None)  # Changed to city field
    available = models.BooleanField(default=True)  # True if they are available for delivery
    assigned_orders = models.IntegerField(default=0)  # Number of orders they are handling
    assigned_time = models.DateTimeField(null=True, blank=True)  # Track last delivery time

    
    def __str__(self):
        return f"{self.name} - {self.address_city}"
    

    def is_available(self):
        return (self.available or self.assigned_time+timedelta(minutes=30) <= timezone.now()) & (self.assigned_orders < 3)
    

    def set_delivery_person(self):
        if self:  
            print(self.name)
            self.assigned_orders += 1
            self.available = False  # Immediately mark the delivery person unavailable
            if self.assigned_orders == 1: 
                self.assigned_time = timezone.now() #set the assigned time (only if it's the first order)
            self.save()
        else:
            raise ValueError("No delivery personnel available for this postal code.")
        

    def delivery_done(self):
        self.assigned_orders -= 1
        if self.assigned_orders == 0:
            self.available = True  # Make the delivery person available
        self.save()

