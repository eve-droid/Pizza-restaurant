from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.db.models import Q
from app.orders.models import Order


class Delivery(models.Model):
    order = models.ForeignKey('orders.order', on_delete=models.CASCADE)
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

