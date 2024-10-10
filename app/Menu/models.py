from django.db import models


class Pizza(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.CharField(max_length=200, default='')
    is_vegetarian = models.BooleanField(default=False)

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

        
class All_Ingredients(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    vegetarian = models.BooleanField(default=False)

    def __str__(self):
        return self.name
