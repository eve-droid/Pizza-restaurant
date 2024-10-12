from django import forms
from .models import Order, OrderItem



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['discount_code']

    discount_code = forms.CharField(max_length=15, required=False)

    
    def save(self, commit=True,customer = None):
        order = super().save(commit=False)

        if customer:
            order.customer = customer

        discount_code = self.cleaned_data.get('discount_code')

        if commit:
            order.save()

        return order
    

    
# Form to handle ordering pizzas
class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['pizza', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 0, 'value': 0}),
        }

# Formset to handle multiple OrderItems
OrderItemFormSet = forms.inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,  #no. of empty forms
    can_delete=True
)