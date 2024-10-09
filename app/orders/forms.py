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

        try:
            order.apply_discount(discount_code)
        except ValueError as e:
            raise forms.ValidationError(str(e))

        if commit:
            order.save()

        return order
    
class OrderItemFormSet(forms.BaseInlineFormSet):
    def save(self, commit=True):
        order_items = super().save(commit=False)
        for order_item in order_items:
            order_item.save()

        if commit:
            self.instance.save()
        return order_items
    
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
    extra=1,  # Number of empty forms
    can_delete=True  # Allow removing pizzas from the order
)