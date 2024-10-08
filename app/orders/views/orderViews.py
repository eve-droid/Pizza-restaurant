from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from app.customers.models import Customer
from app.discounts.models import Discount
from app.orders.forms import OrderForm
from app.orders.models import Delivery, Dessert, Drink, Order, OrderItem, Pizza, DeliveryPerson

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
        

