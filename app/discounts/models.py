from datetime import datetime
from django.db import models

#each discount is unique to a customer
class Discount(models.Model):
    discount_code = models.CharField(max_length=15, unique = True)
    discount = models.IntegerField(max_digits=2) #discount percentage
    used = models.BooleanField(default=False)
    end_date = models.DateTimeField(null=True, blank=True)


    def is_not_expired(self):
        return not self.used and (self.end_date > datetime.now() or self.end_date == None)
