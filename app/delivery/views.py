import json
from django.http import JsonResponse
from django.shortcuts import  render

from app.delivery.services.deliveryPersonService import DeliveryPersonService
from app.delivery.services.deliveryService import DeliveryService
from app.orders.services.orderServiceFactory import ServiceFactory

factory = ServiceFactory()
order_service = factory.create_order_service()
delivery_service = DeliveryService()
deliveryPerson_service = DeliveryPersonService()

def order_success(request, pk):
    order = order_service.get_order_by_id(pk)

    if request.method == 'POST':
        ##
        delivery = delivery_service.get_delivery_by_order(order)

        data = json.loads(request.body)
        status = data.get('status')

        if status == 'Cancelled':
            order_service.cancel_order(order)
        else:
            order_service.update_order_status(order)

    else:
        delivery = delivery_service.create_delivery(order)
        delivery_service.set_delivery_time(delivery)
        deliveryPerson_service.assign_delivery_person(delivery, order)


    return render(request, 'delivery/orderSuccess.html', {
        'order': order,
        'order_time': order.order_time,
        'estimated_delivery_time': delivery.estimated_delivery_time.strftime('%H:%M:') if delivery.estimated_delivery_time else 'Not available',
        'delivery_person': delivery.delivery_person, 
    })


    






