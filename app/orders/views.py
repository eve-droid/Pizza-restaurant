from decimal import Decimal
from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import timedelta


from app.customers.models import Customer
from app.discounts.models import Discount
from .forms import OrderForm
from .models import Delivery, Dessert, Drink, Order, OrderItem, Pizza, DeliveryPerson
from django.http import JsonResponse

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
        try:
            customer = Customer.objects.get(user=user)
            print("Customer instance retrieved:", customer)
        except Customer.DoesNotExist:
            print("Customer does not exist for user:", user)
            return redirect('create_order')  # Or handle appropriately

        if customer.is_birthday_today():
            free_item_eligible = True
            print("Customer is eligible for a free item due to birthday.")
        else:
            customer.had_BD_gift = False
            customer.save()
            print("Customer birthday gift reset.")

        if customer.is_eligible_for_discount():
            additional_discount = True
            print("Customer is eligible for an additional discount.")

    if request.method == 'POST':
        form = OrderForm(request.POST)
        print("Form submitted.")

        if form.is_valid():
            print("Form is valid.")
            customer_instance = get_object_or_404(Customer, user=request.user)
            order = form.save(commit=False)
            order.customer = customer_instance
            order.save()
            print(f"Order saved with ID: {order.id}")

            quantities = request.POST
            for key in quantities.keys():
                if key.startswith('pizzaQuantities['):
                    pizza_id = key.split('[')[1][:-1]
                    quantity = int(quantities[key])
                    if quantity > 0:
                        pizza = Pizza.objects.get(id=pizza_id)
                        order_item = OrderItem(order=order, pizza=pizza, quantity=quantity)
                        order_item.save()
                        customer.count_pizza += quantity
                        customer.save()
                        if free_item_eligible and (cheapest_pizza is None or cheapest_pizza.calculate_price() > pizza.calculate_price()):
                            cheapest_pizza = pizza
                        print(f"Added pizza: {pizza.name}, Quantity: {quantity}")
                elif key.startswith('drinkQuantities['):
                    drink_id = key.split('[')[1][:-1]
                    quantity = int(quantities[key])
                    if quantity > 0:
                        drink = Drink.objects.get(id=drink_id)
                        order_item = OrderItem(order=order, drink=drink, quantity=quantity)
                        order_item.save()
                        if free_item_eligible and (cheapest_drink is None or cheapest_drink.price > drink.price):
                            cheapest_drink = drink
                        print(f"Added drink: {drink.name}, Quantity: {quantity}")
                elif key.startswith('dessertQuantities['):
                    dessert_id = key.split('[')[1][:-1]
                    quantity = int(quantities[key])
                    if quantity > 0:
                        dessert = Dessert.objects.get(id=dessert_id)
                        order_item = OrderItem(order=order, dessert=dessert, quantity=quantity)
                        order_item.save()
                        print(f"Added dessert: {dessert.name}, Quantity: {quantity}")

            if free_item_eligible:
                customer.had_BD_gift = True
                customer.save()
                print("Customer has received a birthday gift.")

                if cheapest_pizza:
                    order_item = OrderItem.objects.filter(order=order, pizza=cheapest_pizza).first()
                    if order_item:
                        order_item.delete()
                        print(f"Deleted cheapest pizza: {cheapest_pizza.name}")

                if cheapest_drink:
                    order_item = OrderItem.objects.filter(order=order, drink=cheapest_drink).first()
                    if order_item:
                        order_item.delete()
                        print(f"Deleted cheapest drink: {cheapest_drink.name}")

            order.price = order.get_total_price()
            order.save()
            print(f"Total order price calculated: {order.price}")

            if additional_discount:
                order.price *= Decimal(0.9)
                customer.count_pizza %= 10  # Reset the count of pizzas
                customer.save()
                print(f"Additional discount applied. New price: {order.price}")

            discount_code = request.POST.get('discountCode', '').strip()
            discount_error = None

            if discount_code:
                order.price, discount_error = order.apply_discount(discount_code)
                order.save()
                print(f"Discount applied. New price: {order.price}, Error: {discount_error}")

            if discount_error:
                print(f"Discount error: {discount_error}")
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

            # Handling delivery person assignment
            try:
                order.assign_delivery_person()
                print("Delivery person assigned.")
                print(f"Delivery {DeliveryPerson.id} assigned to order {Order.id}.")
            except ValueError as e:
                print(f"Delivery person assignment error: {e}")
                order.status = 'Pending Delivery'  # Update order status to 'Pending Delivery'
                order.save()
                messages.warning(request, "No delivery person is available. Your order will be processed shortly.")
            
            # Create and save the Delivery instance
            delivery = Delivery(Delivery_order=order)
            delivery.set_delivery_time()
            delivery.save()
            order.delivery_id = delivery.id
            order.save()
            print(f"Delivery created with ID: {delivery.id}")

            # Redirect to order success page
            return redirect('order_success', pk=order.pk)

        else:
            print("Form is invalid.")
            print(form.errors)
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

    else:
        form = OrderForm()

    # Check the dietary information of pizzas
    for pizza in pizzas:
        pizza.is_vegetarian = pizza.check_if_vegetarian()
        pizza.save()
        print(f"{pizza.name} is vegetarian: {pizza.is_vegetarian}")
        
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
    
    # Automatically update the status before rendering the page
    order.auto_update_status()
    
    delivery_person = order.assign_delivery_person()

    # Check if there's a delivery person assigned and calculate estimated delivery time
    delivery_person = order.delivery_person

    if delivery_person:
        order.estimated_delivery_time = order.estimate_delivery_time()  # Update the estimated delivery time
        estimated_time = order.estimated_delivery_time
    else:
        estimated_time = None 
        order.status = 'Pending Delivery'  # Update order status to 'Pending Delivery'
        order.save()

    return render(request, 'orders/orderSuccess.html', {
        'order': order,
        'order_time': order.order_time,
        'estimated_delivery_time': estimated_time.strftime('%H:%M:%S') if estimated_time else 'Not available',
        'delivery_person': delivery_person, 
    })



def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    try:
        order = order.cancel_order()
        order.save()
        print(order.status)
        return JsonResponse({'success': True, 'message': 'Order cancelled successfully.'})
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)})

def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not order.estimated_delivery_time:
        order.estimated_delivery_time()
    
    return JsonResponse({
        'status': order.status,
        'estimated_delivery_time': order.estimated_delivery_time.strftime("%Y-%m-%d %H:%M") if order.estimated_delivery_time else "Not available"
    })

def start_delivery(request, order_id):
    #mark the order as 'Out for Delivery' and set the delivery time
    order = get_object_or_404(Order, id=order_id)
    if order.status == 'Processing':
        delivery = Delivery.objects.create(Delivery_order=order)
        delivery.set_delivery_time()
        order.update_status('Out for Delivery')
        delivery.save()
    return redirect('track_order', order_id=order_id)

def mark_as_delivered(request, order_id):
    #mark the order as delivered
    order = get_object_or_404(Order, id=order_id)
    if order.status == 'Out for Delivery':
        order.update_status('Delivered')
    return redirect('track_order', order_id=order_id)



def assign_delivery_person(order):
    #find available delivery persons for the order's postal code
    available_persons = DeliveryPerson.objects.filter(address_city=order.customer.address_city, available=True)
    
    if available_persons.exists():
        #assign first delivery guy that's available
        delivery_person = available_persons.first()
        delivery_person.assigned_orders += 1
        delivery_person.save()
        
        #update order with delivery info
        order.delivery_person = delivery_person
        order.save()
    else:
        raise ValueError("No delivery personnel available for this postal code.")

def start_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    try:
        assign_delivery_person(order)
        order.status = 'Out for Delivery'
        order.save()
        return JsonResponse({'success': True, 'message': 'Delivery started successfully.'})
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)})
