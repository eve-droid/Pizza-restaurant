from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from app.customers.models import Customer
from .forms import OrderForm
from .models import Delivery, Dessert, Drink, Order, OrderItem, Pizza

@login_required(login_url='/login/')
def create_order(request):
    pizzas = Pizza.objects.all()
    drinks = Drink.objects.all()
    desserts = Dessert.objects.all()
    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():

            customer_instance = get_object_or_404(Customer, user=request.user) 
            order = form.save(commit=False)  # Create the Order instance but do not save it yet
            order.customer = customer_instance  # Set the customer
            
            # Calculate total price before saving the order
        
            order.save()  # Now save the order to get its ID

            quantities = request.POST  # Get all POST data
            for key in quantities.keys():
                if key.startswith('pizzaQuantities['):  
                    pizza_id = key.split('[')[1][:-1]  
                    quantity = int(quantities[key]) 
                    if quantity > 0:
                        pizza = Pizza.objects.get(id=pizza_id)  
                        order_item = OrderItem(order=order, pizza=pizza, quantity=quantity)
                        order_item.save()
                elif key.startswith('drinkQuantities['):  
                    drink_id = key.split('[')[1][:-1]  
                    quantity = int(quantities[key]) 
                    if quantity > 0:
                        drink = Drink.objects.get(id=drink_id)  
                        order_item = OrderItem(order=order, drink=drink, quantity=quantity)
                        order_item.save()
                elif key.startswith('dessertQuantities['):  
                    dessert_id = key.split('[')[1][:-1]  
                    quantity = int(quantities[key]) 
                    if quantity > 0:
                        dessert = Dessert.objects.get(id=dessert_id)  
                        order_item = OrderItem(order=order, dessert=dessert, quantity=quantity)
                        order_item.save()

            order.price = order.get_total_price()

            # Now create and save the Delivery instance
            delivery = Delivery(Delivery_order=order)  # Create a delivery instance
            delivery.set_delivery_time()  # Set the delivery time
            delivery.save()
            order.save()  


            return redirect('order_success') 
    else:
        form = OrderForm()

    return render(request, 'orders/orderForm.html', {
        'form': form,
        'pizzas': pizzas,  
        'drinks': drinks,
        'desserts': desserts,
    })
    

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