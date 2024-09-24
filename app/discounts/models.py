from datetime import datetime
from django.db import models

#each discount is unique to a customer
class Discount(models.Model):
    discount_code = models.CharField(max_length=15, unique = True)
    discount = models.IntegerField() #discount percentage
    used = models.BooleanField(default=False)
    end_date = models.DateTimeField(null=True, blank=True)


    def is_valid(self):

        try:
            discount = Discount.objects.get(discount_code=self.discount_code)
            if discount.used:
                raise ValueError('The dicount code has already been used')
            elif discount.end_date <= datetime.now() or self.end_date is not None:
                raise ValueError('Discount code has expired')
            else:
                return True
        
        except Discount.DoesNotExist:
            raise ValueError('Invalid discount code')
        
        
