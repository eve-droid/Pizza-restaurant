import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from app.delivery.models import Delivery
from app.orders.models import Order


def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == 'POST':
        ##
        delivery = Delivery.objects.filter(order_id=order.id).first()

        data = json.loads(request.body)
        status = data.get('status')

        if status == 'Cancelled':
            cancel_order(order.id)
        else:
            update_status(order.id)

    else:
        delivery = Delivery.objects.create(order_id=order.id)
        delivery.set_delivery_time()
        delivery.assign_delivery_person(order)

    print(order.items.all())
    print(order)
    return render(request, 'delivery/orderSuccess.html', {
        'order': order,
        'order_time': order.order_time,
        'estimated_delivery_time': delivery.estimated_delivery_time.strftime('%H:%M:') if delivery.estimated_delivery_time else 'Not available',
        'delivery_person': delivery.delivery_person, 
    })

def update_status(order_id):

    try:
        order = get_object_or_404(Order, id = order_id)
        order.auto_update_order_status()
        print(order.status)

        return JsonResponse({'status': 'success'})
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Order not found'})


def cancel_order(order_id):
    order = get_object_or_404(Order, id=order_id)
    try:
        order.cancel_order()
        order.save()
        return JsonResponse({'success': True, 'message': 'Order cancelled successfully.'})
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    






