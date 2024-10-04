from django.db import models

class earningReports(models.Model):
    month = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)
    ageMin = models.IntegerField(default = 18)
    ageMax = models.IntegerField(default = 100)
    earnings = models.DecimalField(max_digits=10, decimal_places=2)