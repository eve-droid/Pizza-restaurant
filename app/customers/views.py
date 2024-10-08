from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .models import Customer  # Import the Customer model

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            login(request, user)  # Automatically log the user in after registration
            return redirect('create_order')  # Redirect to the main page after registration
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})
