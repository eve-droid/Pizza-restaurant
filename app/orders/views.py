from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from app.customers.models import Customer
from .forms import OrderForm
from .models import Delivery, Order

@login_required(login_url='/login/')
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            customer_instance = get_object_or_404(Customer, user=request.user)            
            form.save(customer=customer_instance)
            return redirect('order_success')
    else:
        form = OrderForm()
    return render(request, 'orders/orderForm.html', {'form': form})


def order_success(request):
    return render(request, 'orders/orderSuccess.html')

def track_order(request, order_id):
    #View to track the status and estimated delivery time of an order.
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/track_order.html', {
        'order': order,
        'estimated_delivery_time': order.estimate_delivery_time(),
    })

def start_delivery(request, order_id):
    #Mark the order as 'Out for Delivery' and set the delivery time."""
    order = get_object_or_404(Order, id=order_id)
    if order.status == 'Processing':
        delivery = Delivery.objects.create(order=order)
        delivery.set_delivery_time()
        order.update_status('Out for Delivery')
        delivery.save()
    return redirect('track_order', order_id=order_id)

def mark_as_delivered(request, order_id):
    #Mark the order as delivered."""
    order = get_object_or_404(Order, id=order_id)
    if order.status == 'Out for Delivery':
        order.update_status('Delivered')
    return redirect('track_order', order_id=order_id)

def homepage(request):
    return render(request, 'homepage.html')