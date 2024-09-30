from django import forms
from .models import Delivery, Order, Pizza, Drink, Dessert  

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['pizza', 'drink', 'dessert', 'discount_code']

    pizza = forms.ModelChoiceField(queryset=Pizza.objects.all(), required=True, empty_label="Select your pizza")
    drink = forms.ModelChoiceField(queryset=Drink.objects.all(), required=False, empty_label="Select a drink")
    dessert = forms.ModelChoiceField(queryset=Dessert.objects.all(), required=False, empty_label="Select a dessert")
    discount_code = forms.CharField(max_length=15, required=False)

    
    def save(self, commit=True,customer = None):
        order = super().save(commit=False)

        if customer:
            order.customer = customer

        print(f"Saving order with delivery: {order.delivery}, customer: {order.customer}, price: {order.price}")


        discount_code = self.cleaned_data.get('discount_code')

        try:
            order.apply_discount(discount_code)
        except ValueError as e:
            raise forms.ValidationError(str(e))
        

        
        print(f"Saving order with delivery: {order.delivery}, customer: {order.customer}, price: {order.price}")

        # Save the order
        if commit:
            order.save()

        delivery = Delivery(Delivery_order=order)
        delivery.set_delivery_time()
        delivery.save()
        order.delivery = delivery

        order.pizzas.add(self.cleaned_data.get('pizza'))
        order.drinks.add(self.cleaned_data.get('drink'))
        order.desserts.add(self.cleaned_data.get('dessert'))

        order.price = order.get_total_price()
        print(order.price)

        if commit:
            order.save()

        

        return order