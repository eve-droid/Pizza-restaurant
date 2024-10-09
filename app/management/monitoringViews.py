from django.http import JsonResponse
from django.shortcuts import render
from app.orders.models import Order


def monitoring(request):

    if request.method == 'POST':
        orders = Order.objects.filter(status = 'Your order is being prepared' or "Processing")

        ordersList = []
        for order in orders:
            orderItems = order.items.all()

            itemsList = []
            for item in orderItems:
                itemsList.append({
                    'name': item.pizza.name if item.pizza else item.dessert.name if item.dessert else item.drink.name,
                    'quantity': item.quantity
                })

            print(order.id)
            ordersList.append({
                'id': order.id,
                'customer_name': order.customer.name,
                'status': order.status,
                'items': itemsList
            })


        return JsonResponse(ordersList, safe=False)     
      
    return render(request, 'management/monitoring.html')
