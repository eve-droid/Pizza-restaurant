from django.shortcuts import render, redirect
from .forms import OrderForm

def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('order_success')
    else:
        form = OrderForm()
    return render(request, 'orders/orderForm.html', {'form': form})

def order_success(request):
    return render(request, 'orders/orderSuccess.html')