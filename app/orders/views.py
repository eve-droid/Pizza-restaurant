from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from app.Menu.services.menuService import MenuService
from app.customers.customerService import CustomerService
from app.discounts.discountService import DiscountService
from app.orders.forms import OrderForm
from app.orders.services.orderItemService import OrderItemService
from app.orders.services.orderServiceFactory import ServiceFactory


factory = ServiceFactory()
order_service = factory.create_order_service()
orderItem_service = OrderItemService()
customer_service = CustomerService()
menu_service = MenuService()
discount_service = DiscountService()

@login_required(login_url='/login/')
def create_order(request):
    pizzas = menu_service.get_all_pizzas()
    drinks = menu_service.get_all_drinks()
    desserts = menu_service.get_all_desserts()
    customer = customer_service.get_customer_by_user(request.user)

    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            #assign customer to order
            order = form.save(commit=False)
            order.customer = customer
            order_service.update_order(order)

            calculate_total_price(request, order)
            print(order.price)

            return redirect('order_success', pk=order.pk)

        else:
            return render(request, 'orders/orderForm.html', {
                'form': form,
                'pizzas': pizzas,
                'drinks': drinks,
                'desserts': desserts,
                'additional_discount': customer_service.is_eligible_for_discount(customer),
                'free_item_eligible': customer_service.is_birthday_today(customer),
            })


    else:
        form = OrderForm()
        
    return render(request, 'orders/orderForm.html', {
        'form': form,
        'pizzas': pizzas,  
        'drinks': drinks,
        'desserts': desserts,
        'additional_discount': customer_service.is_eligible_for_discount(customer),
        'free_item_eligible': customer_service.is_birthday_today(customer),
    })



def calculate_total_price(request, order):

    eligible_for_loyalty_discount = customer_service.is_eligible_for_discount(order.customer) #check if eleigible before calling update_order_items because customer.count_pizza is updated there

    customer = order.customer
    quantities = request.POST
    orderItem_service.populate_order_items(customer, quantities, order) #populate order.items

    order_service.get_total_price(order)

    order_service.apply_BD_gift(order) #apply free gifts if Bday

    order_service.loyaltyDiscount(order, eligible_for_loyalty_discount)

    discount_code = request.POST.get('discountCode', '').strip()
    order_service.apply_discount(order, discount_code)



    

    

def validate_discount_code(request):
    code = request.GET.get('code', '').strip() 
    has_discount_code = request.GET.get('has_discount_code', 'false').lower() == 'true'

    try:
        discount = discount_service.get_discount_by_code(code)
        if discount_service.is_valid(discount) and not has_discount_code:
            return JsonResponse({'valid': True, 'percentage': float(discount.percentage)})
        elif has_discount_code:
            return JsonResponse({'valid': False, 'message': 'A discount code has already been applied.'})
        else:
            return JsonResponse({'valid': False, 'message': 'This discount code is not valid.'})
    except Exception:
        return JsonResponse({'valid': False, 'message': 'This discount code does not exist.'})
        

