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
        vegetarian_ingredients = ['mozzarella', 'tomato sauce', 'basil','zucchini', 'eggplant', 'peppers', 'pineaplle', 'onions', 'mushrooms', 'olives', 'ricotta', 'parmesan']
        for ingredient in self.get_ingredients():
            if ingredient not in vegetarian_ingredients:
                return False
        return True
    
    def check_if_vegan(self):
        # Check if the pizza is vegan
        vegan_ingredients = ['tomato sauce', 'basil','zucchini', 'eggplant', 'peppers', 'pineaplle', 'onions', 'mushrooms', 'olives']
        for ingredient in self.get_ingredients():
            if ingredient not in vegan_ingredients:
                return False
        return True
    
    def get_ingredients(self):
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
        ('Making', 'Making'),  # Added new status for Making
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
            self.status = 'Making'
            self.save()

        # Step 2: After 15 minutes (total 20 mins), change from "Making" to "Out for Delivery"
        if self.status == 'Making' and time_since_order > timedelta(minutes=20):
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

    def assign_delivery_person(self):
        # Get all available delivery persons for the customer’s city
        available_person = DeliveryPerson.objects.filter(available=True, city=self.customer.address_city).first()

        if available_person:
            available_person.assign_delivery(self)
        else:
            raise ValueError("No available delivery person for this city.")

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
    city = models.CharField(max_length=100)  # Changed from postal_code to city
    available = models.BooleanField(default=True)
    assigned_orders = models.IntegerField(default=0)
    last_assigned_time = models.DateTimeField(null=True, blank=True)


    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    def is_available(self, customer_city):
        # Check if delivery person is available and assigned to the correct city
        return self.available and self.assigned_orders < 3 and self.city == customer_city

    
    def assign_delivery(self, order):
        """
        Assign delivery to this person and mark them unavailable for 30 minutes.
        """
        self.assigned_orders += 1
        self.available = False
        self.last_assigned_time = timezone.now()
        self.save()

        # Assign this delivery person to the order
        order.delivery_person = self
        order.estimated_delivery_time = timezone.now() + timedelta(minutes=30)  # Set estimated delivery time
        order.save()

        # Schedule them to be available again after 30 minutes
        self._schedule_availability()

    def _schedule_availability(self):
        """
        Automatically make the delivery person available after 30 minutes.
        This will require a periodic task (using Celery or Django's built-in timing mechanism).
        """
        # After 30 minutes, mark the delivery person as available again
        available_time = self.last_assigned_time + timedelta(minutes=30)
        if timezone.now() >= available_time:
            self.available = True
            self.assigned_orders -= 1
            self.save()

