from django.utils import timezone
from django.db import models

#each discount is unique to a customer
class Discount(models.Model):
    discount_code = models.CharField(max_length=15, unique = True)
    percentage = models.IntegerField() #discount percentage
    used = models.BooleanField(default=False)
    end_date = models.DateTimeField(null=True, blank=True)


    def is_valid(self):

        try:
            if self.used:
                return False
            elif self.end_date and self.end_date <= timezone.now() :
                return False
            else:
                return True
        
        except Discount.DoesNotExist:
            print('does not exist')
            return False
        
        
