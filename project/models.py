from django.db import models

class Pizza(models.Model):
    pizza_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

class Dessert(models.Model):
    dessert_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)

class Drink(models.Model):
    drink_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    customer_id = models.IntegerField()
    pizzas = models.ManyToManyField(Pizza)
    desserts = models.ManyToManyField(Dessert, blank=True)
    drinks = models.ManyToManyField(Drink, blank=True)
    delivery_id = models.IntegerField()
    price = models.IntegerField()
    order_time = models.DateTimeField()
    delivery_time = models.DateTimeField()
    delivery_address = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    
class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    birthday = models.DateField()
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    number_pizza = models.IntegerField()

class Delivery(models.Model):
    delivery_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    number_order = models.IntegerField()
    status = models.CharField(max_length=100)