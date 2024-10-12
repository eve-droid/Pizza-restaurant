from django.db import models


class Delivery(models.Model):
    order = models.ForeignKey('orders.order', on_delete=models.CASCADE)
    delivery_person = models.ForeignKey('DeliveryPerson', on_delete=models.SET_NULL, null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)


class DeliveryPerson(models.Model):
    name = models.CharField(max_length=100)
    postal_code_area = models.CharField(max_length=100, null = True, default=None)
    available = models.BooleanField(default=True)
    assigned_orders = models.IntegerField(default=0)
    assigned_time = models.DateTimeField(null=True, blank=True)

    
    def __str__(self):
        return f"{self.name} - {self.address_city}"
    



