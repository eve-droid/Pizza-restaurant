from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from app.customers.models import Customer
from app.discounts.models import Discount
from .forms import OrderForm
from .models import Delivery, Dessert, Drink, Order, OrderItem, Pizza, DeliveryPerson

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
        except Customer.DoesNotExist:
            return redirect('create_order')

        if customer.is_birthday_today():
            free_item_eligible = True
        else:
            customer.had_BD_gift = False
            customer.save()

        if customer.is_eligible_for_discount():
            additional_discount = True

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            customer_instance = get_object_or_404(Customer, user=request.user)
            order = form.save(commit=False)
            order.customer = customer_instance
            order.save()

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

            if additional_discount:
                order.price *= Decimal(0.9)
                customer.count_pizza %= 10
                customer.save()

            discount_code = request.POST.get('discountCode', '').strip()
            discount_error = None

            if discount_code:
                order.price, discount_error = order.apply_discount(discount_code)
                order.save()

            if discount_error:
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
                assign_delivery_person(order)
                update_delivery_persons()  # Call the update function here
            except ValueError as e:
                order.status = 'Pending Delivery'
                order.save()

            # Create and save the Delivery instance
            delivery = Delivery(Delivery_order=order)
            delivery.set_delivery_time()
            delivery.save()
            order.delivery_id = delivery.id
            order.save()

            return redirect('order_success', pk=order.pk)

        else:
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

    for pizza in pizzas:
        pizza.is_vegetarian = pizza.check_if_vegetarian()
        pizza.save()
        
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
    code = request.GET.get('code', '').strip() 
    has_discount_code = request.GET.get('has_discount_code', 'false').lower() == 'true'

    try:
        discount = Discount.objects.get(discount_code=code)
        if discount.is_valid() and not has_discount_code:
            return JsonResponse({'valid': True, 'percentage': float(discount.percentage)})
        elif has_discount_code:
            return JsonResponse({'valid': False, 'message': 'A discount code has already been applied.'})
        else:
            return JsonResponse({'valid': False, 'message': 'This discount code is not valid.'})
    except Discount.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'This discount code does not exist.'})

def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    order.auto_update_status()
    
    delivery_person = order.delivery_person

    if delivery_person:
        order.estimated_delivery_time = order.estimate_delivery_time()  
        estimated_time = order.estimated_delivery_time
    else:
        estimated_time = None 
        order.status = 'Pending Delivery'  
        order.save()

    return render(request, 'orders/orderSuccess.html', {
        'order': order,
        'order_time': order.order_time,
        'estimated_delivery_time': estimated_time.strftime('%H:%M:') if estimated_time else 'Not available',
        'delivery_person': delivery_person, 
    })

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    try:
        order.cancel_order()
        order.save()
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
    order = get_object_or_404(Order, id=order_id)
    
    if order.status == 'Processing':
        delivery = Delivery.objects.create(Delivery_order=order)
        delivery.set_delivery_time()
        order.update_status('Out for Delivery')
        delivery.save()
    return redirect('track_order', order_id=order_id)

def mark_as_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status == 'Out for Delivery':
        order.deliver_order()  # Call the deliver_order method
        order.update_status('Delivered')
    return redirect('track_order', order_id=order_id)

def assign_delivery_person(order):
    # Get only available delivery persons with no ongoing orders (assigned_orders == 0)
    available_persons = DeliveryPerson.objects.filter(address_city=order.customer.address_city, available=True, assigned_orders=0)
    
    if available_persons.exists():
        delivery_person = available_persons.first()  # Assign the first available person
        delivery_person.assign_delivery(order)  # Call the method to assign and update their status
        return delivery_person
    else:
        raise ValueError("No delivery personnel available for this postal code.")

def update_delivery_persons():
    # Example logic to update delivery persons' availability or assigned orders
    for person in DeliveryPerson.objects.all():
        if person.assigned_orders > 0:
            person.assigned_orders -= 1  # Decrement the count
            if person.assigned_orders == 0:
                person.available = True  # Mark as available if no orders are assigned
        else:
            person.available = True  # Mark as available if not assigned any orders
        person.save()
