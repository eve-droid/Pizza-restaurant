from django import forms
from .models import Order, Customer  # Assuming you have these models

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'pizza', 'drinks', 'desserts', 'discount_code']

    pizza = forms.ChoiceField(choices=[('margherita', 'Margherita'), ('napoletana', 'Napoletana'), ('bufalina', 'Bufalina'), ('vegetarian', 'Vegetarian'), ('calzone', 'Calzone'), ('pepperoni', 'Pepperoni'), ('quattro fromaggi', 'Quattro Fromaggi'), ('primavera', 'Primavera'), ('romana', 'Romana'), ('caprese', 'Caprese'), ('capricciosa', 'Capricciosa')], required=True)
    drinks = forms.ChoiceField(choices=[('coke', 'Coke'), ('fanta', 'Fanta'), ('sprite', 'Sprite'), ('pepsi', 'Pepsi'), ('water', 'Water'), ('orange juice', 'Orange Juice')], required=False)
    desserts = forms.ChoiceField(choices=[('tiramisu', 'Tiramisu'), ('panna cotta', 'Panna Cotta'), ('gelato', 'Gelato')], required=False)
    discount_code = forms.CharField(max_length=15, required=False)
