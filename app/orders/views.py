from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import OrderForm

@login_required(login_url='/login/')
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