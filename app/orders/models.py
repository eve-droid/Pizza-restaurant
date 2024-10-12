from django.db import models
from app.customers.models import Customer
from app.Menu.models import Pizza, Drink, Dessert



class Order(models.Model):
    Status_Choices = [
        ('Processing', 'Processing'),
        ('Your Order is being prepared', 'Your Order is being prepared'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    order_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=Status_Choices, default='Processing')
    has_discount_code = models.BooleanField(default=False)



class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name='items', on_delete=models.CASCADE)
    pizza = models.ForeignKey('Menu.Pizza', null=True, blank=True, on_delete=models.CASCADE)
    drink = models.ForeignKey('Menu.Drink', null=True, blank=True, on_delete=models.CASCADE)
    dessert = models.ForeignKey('Menu.Dessert', null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        if self.pizza is not None:
            return f"{self.quantity} x {self.pizza.name} for Order #{self.order.id}" 
        elif self.drink is not None:
            return f"{self.quantity} x {self.drink.name} for Order #{self.order.id}"
        elif self.dessert is not None:
            return f"{self.quantity} x {self.dessert.name} for Order #{self.order.id}"   


