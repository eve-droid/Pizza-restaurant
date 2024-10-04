from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


from app.customers.models import Customer
from app.discounts.models import Discount
from .forms import OrderForm
from .models import Delivery, Dessert, Drink, Order, OrderItem, Pizza

@login_required(login_url='/login/')
def create_order(request):
    pizzas = Pizza.objects.all()
    drinks = Drink.objects.all()
    desserts = Dessert.objects.all()
    user = request.user
    additional_discount = False
    free_item_eligible = False
    cheapest_pizza = None
    cheapest_drink = None
    if user.is_authenticated:
        customer = Customer.objects.get(user=user)

        if customer.is_birthday_today():
            free_item_eligible = True

        if customer.is_eligible_for_discount():
            additional_discount = True
            print('Eligible for discount')

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
                        # Update the count_pizza field of the customer
                        customer.count_pizza += quantity
                        customer.save()
                        if (free_item_eligible and (cheapest_pizza is None or cheapest_pizza.calculate_price() > pizza.calculate_price())):
                            cheapest_pizza = pizza
                elif key.startswith('drinkQuantities['):  
                    drink_id = key.split('[')[1][:-1]  
                    quantity = int(quantities[key]) 
                    if quantity > 0:
                        drink = Drink.objects.get(id=drink_id)  
                        order_item = OrderItem(order=order, drink=drink, quantity=quantity)
                        order_item.save()
                        if free_item_eligible and (cheapest_drink is None or cheapest_drink.price > drink.price):
                            cheapest_drink = drink
                elif key.startswith('dessertQuantities['):  
                    dessert_id = key.split('[')[1][:-1]  
                    quantity = int(quantities[key]) 
                    if quantity > 0:
                        dessert = Dessert.objects.get(id=dessert_id)  
                        order_item = OrderItem(order=order, dessert=dessert, quantity=quantity)
                        order_item.save()

            if free_item_eligible:
                customer.had_BD_gift = True
                customer.save()
                if cheapest_pizza:
                    order_item = OrderItem.objects.filter(order=order, pizza=cheapest_pizza).first()
                    if order_item:
                        order_item.delete()
                if cheapest_drink:
                    order_item = OrderItem.objects.filter(order=order, drink=cheapest_drink).first()
                    if order_item:
                        order_item.delete()
            
            order.price = order.get_total_price()
            order.save()

            # Apply 10% discount if the customer is eligible
            if additional_discount:
                order.price *= Decimal(0.9)
                customer.count_pizza %= 10 # Reset the count of pizzas
                customer.save()

            discount_code = request.POST.get('discountCode', '').strip()
            discount_error = None

            # Server-side validation of the discount code
            if discount_code:
                order.price, discount_error = order.apply_discount(discount_code)
                order.save()

            if discount_error:
                # If there's a discount error, show it to the user
                return render(request, 'orders/orderForm.html', {
                    'form': form,
                    'pizzas': pizzas,
                    'drinks': drinks,
                    'desserts': desserts,
                    'discount_error': discount_error,
                    'additional_discount': additional_discount,
                    'free_item_eligible': free_item_eligible,
                    'cheapest_pizza': cheapest_pizza,
                    'cheapest_drink': cheapest_drink,  
                })
            
            #check the dietery of pizzas
            for pizza in pizzas:
                pizza.is_vegan = pizza.check_if_vegan()
                pizza.is_vegetarian = pizza.check_if_vegetarian()
                pizza.save()
                print(pizza.is_vegetarian)
            # Now create and save the Delivery instance
            delivery = Delivery(Delivery_order=order)  # Create a delivery instance
            delivery.set_delivery_time()  # Set the delivery time
            delivery.save()
            order.save()  


            return redirect('order_success', pk=order.pk)
    else:
        form = OrderForm()

    return render(request, 'orders/orderForm.html', {
        'form': form,
        'pizzas': pizzas,  
        'drinks': drinks,
        'desserts': desserts,
        'additional_discount': additional_discount,
        'free_item_eligible': free_item_eligible,
        'cheapest_pizza': cheapest_pizza,
        'cheapest_drink': cheapest_drink,
    })


def validate_discount_code(request):
    code = request.GET.get('code', '').strip()  # Get the code from the GET request
    has_discount_code = request.GET.get('has_discount_code', 'false').lower() == 'true'

    try:
        discount = Discount.objects.get(discount_code=code)  # Check if the discount exists in the database
        if discount.is_valid() and not has_discount_code: # Check if the discount is valid and has not been used 
            return JsonResponse({'valid': True, 'percentage': float(discount.percentage)})
        elif has_discount_code:
            return JsonResponse({'valid': False, 'message': 'A discount code has already been applied.'})
        else:
            return JsonResponse({'valid': False, 'message': 'This discount code is not valid.'})
    except Discount.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'This discount code does not exist.'})

    

def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    return render(request, 'orders/orderSuccess.html', {'order': order})

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