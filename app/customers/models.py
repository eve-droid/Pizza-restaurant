from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default=None)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    birthday = models.DateField()
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    count_pizza = models.IntegerField(default = 0)

    def is_eligible_for_discount(self):
        return self.count_pizza >= 10