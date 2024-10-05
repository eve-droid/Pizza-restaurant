import json

from django.http import JsonResponse
from django.shortcuts import render
from django.db.models.functions import ExtractMonth
from datetime import date, datetime

from app import customers
from app.customers.models import Customer
from app.orders.models import Order

def generate_earning_report(request):
    earningReport = {}
    print('generate_earning_report')

    if request.method == 'POST':
        orders = Order.objects.all()
        print('filterLoaded')
        #get filters
        data = json.loads(request.body)

        todayDate = date.today()

        month = int(data.get('month'))
        orders = Order.objects.annotate(month=ExtractMonth('order_time')).filter(month = month)

        region = data.get('region')
        if(region != 'All'):
            orders = orders.filter(customer__address_city = region)

        gender = data.get('gender')
        if(gender != 'All'):
            orders = orders.filter(customer__gender = gender)

        age_min = int(data.get('ageFrom'))
        latestBirthday = todayDate.replace(year=todayDate.year - age_min-1) 
        print(latestBirthday)
        print(orders)

        age_max = int(data.get('ageTo'))
        earliestBirthday = todayDate.replace(year=todayDate.year - age_max)
        orders = orders.filter(customer__birthday__range = (earliestBirthday, latestBirthday))
        print(earliestBirthday)
        print(orders)

        print('got filters')

        earningReport = {
            'month': month,
            'region': region,
            'gender': gender,
            'ageMin': age_min,
            'ageMax': age_max,
            'earnings': sum(order.price for order in orders)
        }

        return JsonResponse({'earningReport': earningReport})
    
    cityList = []
    for customer in Customer.objects.all():
        cityList.append(customer.address_city)
    
    return render(request, 'management/earningReports.html', {'cityList': cityList})
        

        
