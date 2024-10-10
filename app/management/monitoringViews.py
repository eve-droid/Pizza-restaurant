from django.http import JsonResponse
from django.shortcuts import render

from app.orders.services.orderItemService import OrderItemService
from app.orders.services.orderServiceFactory import ServiceFactory


def monitoring(request):

    if request.method == 'POST':

        status = ['Your order is being prepared', 'Processing']

        factory = ServiceFactory()
        order_service = factory.create_order_service()
        orderItem_service = OrderItemService()

        orders = order_service.get_all_orders()
        orders = order_service.filter_orders_by_status(status, orders)

        ordersList = []
        for order in orders:
            orderItems = orderItem_service.get_order_items(order)

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
