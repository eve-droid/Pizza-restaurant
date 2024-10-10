import json

from django.http import JsonResponse
from django.shortcuts import render
from datetime import date

from app.customers.customerService import CustomerService
from app.orders.services.orderServiceFactory import ServiceFactory

def generate_earning_report(request):
    earningReport = {}
    print('generate_earning_report')

    if request.method == 'POST':
        factory = ServiceFactory()
        order_service = factory.create_order_service()

        status = ['Processing', 'Your order is being prepared','Out for Delivery', 'Delivered']

        orders = order_service.filter_orders_by_status(status)#get all orders that were not cancelled

        #get filters
        data = json.loads(request.body)

        todayDate = date.today()

        #filter by month
        month = int(data.get('month'))
        orders = order_service.filter_orders_by_month(month, orders)

        #filter by region
        region = data.get('region')
        if(region != 'All'):
            orders = order_service.filter_orders_by_region(region, orders)

        #filter by gender
        gender = data.get('gender')
        if(gender != 'All'):
            orders = order_service.filter_orders_by_gender(gender, orders)

        #filter by age
        age_min = int(data.get('ageFrom'))
        latestBirthday = todayDate.replace(year=todayDate.year - age_min-1) 
        age_max = int(data.get('ageTo'))
        earliestBirthday = todayDate.replace(year=todayDate.year - age_max)
        orders = order_service.filter_orders_by_customer_age(earliestBirthday, latestBirthday, orders)


        earningReport = {
            'month': month,
            'region': region,
            'gender': gender,
            'ageMin': age_min,
            'ageMax': age_max,
            'earnings': sum(order.price for order in orders)
        }

        return JsonResponse({'earningReport': earningReport})
    
    customer_service = CustomerService()
    cityList = []
    for customer in customer_service.get_all_customers():
        cityList.append(customer.address_city)
    
    return render(request, 'management/earningReports.html', {'cityList': cityList})
        

