from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default=None)
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    birthday = models.DateField()
    phone = models.CharField(max_length=100)
    address_number_street = models.CharField(max_length=100)
    address_city = models.CharField(max_length=100)
    address_postal_code = models.CharField(max_length=100)
    count_pizza = models.IntegerField(default = 0)
    last_BD_gift = models.DateField(null=True, default=None)

    def __str__(self):
        return self.name

    def is_eligible_for_discount(self):
        return self.count_pizza >= 10

    def is_birthday_today(self):
        print(self.last_BD_gift != datetime.now().date())
        print(self.birthday == datetime.now().strftime('%m-%d'))
        # compare the dates without year
        return self.birthday.strftime('%m-%d') == datetime.now().strftime('%m-%d') and (self.last_BD_gift is None or self.last_BD_gift != datetime.now().date())