from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from app.customers.models import Customer

class CustomUserCreationForm(UserCreationForm):

    name = forms.CharField(max_length=100, required=True)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], required=True)
    birthday = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2025)), required=True)
    phone = forms.CharField(max_length=100, required=True)
    address_number_street = forms.CharField(max_length=100, required=True)
    address_city = forms.CharField(max_length=100, required=True)  
    address_postal_code = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

        customer = Customer(
            user=user,
            name=self.cleaned_data.get('name'),
            phone=self.cleaned_data.get('phone'),
            birthday=self.cleaned_data.get('birthday'),
            address_number_street=self.cleaned_data.get('address_number_street'),
            address_city=self.cleaned_data.get('address_city'),
            address_postal_code=self.cleaned_data.get('address_postal_code'),  
            gender=self.cleaned_data.get('gender'),
        )
        if commit:
            customer.save()

        return user
