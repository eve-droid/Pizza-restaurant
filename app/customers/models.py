from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    birthday = models.DateField()
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    count_pizza = models.IntegerField()

    def is_eligible_for_discount(self):
        return self.count_pizza >= 10