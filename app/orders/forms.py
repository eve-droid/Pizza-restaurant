from django import forms
from .models import Order, Pizza, Drink, Dessert  

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['pizza', 'drink', 'dessert', 'discount_code']

    pizza = forms.ModelChoiceField(queryset=Pizza.objects.all(), required=True, empty_label="Select your pizza")
    drink = forms.ModelChoiceField(queryset=Drink.objects.all(), required=False, empty_label="Select a drink")
    dessert = forms.ModelChoiceField(queryset=Dessert.objects.all(), required=False, empty_label="Select a dessert")
    discount_code = forms.CharField(max_length=15, required=False)

    
    def save(self, commit=True):
        order = super().save(commit=False)

        discount_code = self.cleaned_data.get('discount_code')

        try:
            order.apply_discount(discount_code)
        except ValueError as e:
            raise forms.ValidationError(str(e))

        # Save the order
        if commit:
            order.save()

        return order