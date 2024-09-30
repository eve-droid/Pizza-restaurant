from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from app.customers.models import Customer

class CustomUserCreationForm(UserCreationForm):

    name = forms.CharField(max_length=100)
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    birthday = forms.DateField(widget=forms.SelectDateWidget())
    phone = forms.CharField(max_length=100)
    address = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    
        

    def save(self, commit=True):
        user = super().save(commit=False)  # Use the super method to create the user
        
        if commit:
            user.save()

        customer = Customer(
            user=user,
            name=self.cleaned_data.get('name'),
            phone=self.cleaned_data.get('phone'),
            address=self.cleaned_data.get('address'),
            birthday=self.cleaned_data.get('birthday'),
            gender=self.cleaned_data.get('gender'),
        )
        if commit:
            customer.save()

        return user