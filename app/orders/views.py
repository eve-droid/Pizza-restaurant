from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from app.customers.models import Customer
from app.discounts.models import Discount
from app.orders.forms import OrderForm
from app.orders.models import Dessert, Drink, OrderItem, Pizza

cheapest_pizza = None
cheapest_drink = None

@login_required(login_url='/login/')
def create_order(request):
    pizzas = Pizza.objects.all()
    drinks = Drink.objects.all()
    desserts = Dessert.objects.all()
    customer = get_object_or_404(Customer, user=request.user)
    if customer.is_birthday_today():
        print('it is birthday')
    if customer.is_eligible_for_discount():
        print('10% discount')

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            #assign customer to order
            order = form.save(commit=False)
            order.customer = customer
            order.save()

            print('ok')
            calculate_total_price(request, order)
            print(order.price)

            return redirect('order_success', pk=order.pk)

        else:
            return render(request, 'orders/orderForm.html', {
                'form': form,
                'pizzas': pizzas,
                'drinks': drinks,
                'desserts': desserts,
                'additional_discount': customer.is_eligible_for_discount(),
                'free_item_eligible': customer.is_birthday_today(),
                'cheapest_pizza': cheapest_pizza,
                'cheapest_drink': cheapest_drink,
            })

    else:
        form = OrderForm()
        
    return render(request, 'orders/orderForm.html', {
        'form': form,
        'pizzas': pizzas,  
        'drinks': drinks,
        'desserts': desserts,
        'additional_discount': customer.is_eligible_for_discount(),
        'free_item_eligible': customer.is_birthday_today(),
        'cheapest_pizza': cheapest_pizza,
        'cheapest_drink': cheapest_drink,
    })



def calculate_total_price(request, order):

    eligible_for_loyalty_discount = order.customer.is_eligible_for_discount() #check if eleigible before calling update_order_items bc customer.count_pizza is updated there

    print(order.items.all())
    update_order_items(request, order)
    print(order.items.all())

    print(order.price)
    order.price = order.get_total_price()
    order.save()
    print(order.price)
    check_BD(order)
    print(order.price)
    loyaltyDiscount(order, eligible_for_loyalty_discount)
    apply_discount(request, order)


def update_order_items(request, order):
    global cheapest_pizza, cheapest_drink
    customer = order.customer
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
                if customer.is_birthday_today() and (cheapest_pizza is None or cheapest_pizza.calculate_price() > pizza.calculate_price()):
                    cheapest_pizza = pizza
        elif key.startswith('drinkQuantities['):
            drink_id = key.split('[')[1][:-1]
            quantity = int(quantities[key])
            if quantity > 0:
                drink = Drink.objects.get(id=drink_id)
                order_item = OrderItem(order=order, drink=drink, quantity=quantity)
                order_item.save()
                if customer.is_birthday_today() and (cheapest_drink is None or cheapest_drink.price > drink.price):
                    cheapest_drink = drink
        elif key.startswith('dessertQuantities['):
            dessert_id = key.split('[')[1][:-1]
            quantity = int(quantities[key])
            if quantity > 0:
                dessert = Dessert.objects.get(id=dessert_id)
                order_item = OrderItem(order=order, dessert=dessert, quantity=quantity)
                order_item.save()


def check_BD(order):
    customer = order.customer
    if customer.is_birthday_today():
        print('BD')

        if cheapest_pizza:
            order.getFreePizza(cheapest_pizza)
            customer.last_BD_gift = datetime.now().date()
            

        if cheapest_drink:
            order.getFreeDrink(cheapest_drink)
            customer.last_BD_gift = datetime.now().date()

        order.save()
        customer.save()


def loyaltyDiscount(order, eligible_for_loyalty_discount):
    customer = order.customer

    if eligible_for_loyalty_discount:
        order.price *= Decimal(0.9)
        customer.count_pizza %= 10
        customer.save()
        order.save()


def apply_discount(request, order):
    discount_code = request.POST.get('discountCode', '').strip()

    if discount_code: #the discount has been valided in the front end so we don't need to check if it's valid here
        order.price = order.apply_discount(discount_code)
        order.save()


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
        

