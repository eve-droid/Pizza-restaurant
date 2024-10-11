from datetime import datetime, timedelta, timezone
from decimal import Decimal
from django.utils import timezone


class OrderService:
    def __init__(self, customerService, menuService, discountService, deliveryService, deliveryPersonService, orderItemService, orderRepository):
        self.customerService = customerService
        self.menuService = menuService
        self.discountService = discountService
        self.deliveryService = deliveryService
        self.deliveryPersonService = deliveryPersonService
        self.orderItemService = orderItemService
        self.orderRepository = orderRepository

    def get_all_orders(self):
        return self.orderRepository.get_all_orders()

    def get_order(self, order_id):
        return self.orderRepository.get_order_by_id(order_id)

    def update_order(self, order):
        order_saved = self.orderRepository.update_order(order)
        return order_saved
    
    def filter_orders_by_status(self, status, orders):
        return self.orderRepository.filter_orders_by_status(status, orders)
    
    def filter_orders_by_region(self, region, orders):
        return self.orderRepository.filter_orders_by_region(region, orders)
    
    def filter_orders_by_month(self, month, orders):
        return self.orderRepository.filter_orders_by_month(month, orders)
    
    def filter_orders_by_gender(self, gender, orders):
        return self.orderRepository.filter_orders_by_gender(gender, orders)
    
    def filter_orders_by_customer_age(self, earliestBirthday, latestBirthday, orders):
        return self.orderRepository.filter_orders_by_customer_age(earliestBirthday, latestBirthday, orders)
    
    def get_order_items(self, order):
        return self.orderItemService.get_order_items(order)
    
    def get_order_by_id(self, order_id):
        return self.orderRepository.get_order_by_id(order_id)
    
    
    def get_total_price(self, order):
        # Calculate total price of the order
        order.price = 0

        pizzas = self.orderItemService.get_pizzas(order)
        desserts = self.orderItemService.get_desserts(order)
        drinks = self.orderItemService.get_drinks(order)

        for pizza in pizzas:
            order.price += self.menuService.calculate_price(pizza.pizza) * pizza.quantity
        for dessert in desserts:
            order.price += dessert.dessert.price * dessert.quantity
        for drink in drinks:
            order.price += drink.drink.price * drink.quantity

        self.orderRepository.update_order(order)


    def apply_discount(self, order, discount_code):
        if discount_code:
            try:
                discount = self.discountService.get_discount_by_code(discount_code)
                if discount.is_valid() and not order.has_discount_code:
                    order.price *= Decimal(1 - discount.percentage / 100)
                    discount.used = True
                    order.has_discount_code = True
                    order.discountService.update_discount(discount)
                elif order.has_discount_code:
                    print('A discount code has already been applied.')
            except Exception:
                print('This discount code is not valid.')

        self.orderRepository.update_order(order)
    
    def getFreePizza(self, order, pizza):
        order.price -= self.menuService.calculate_price(pizza.pizza)
        self.orderRepository.update_order(order)

    def getFreeDrink(self, order, drink):
        order.price -= drink.drink.price
        self.orderRepository.update_order(order)


    def update_order_status(self, order):
        now = timezone.now()
        time_since_order = now - order.order_time
        delivery = self.deliveryService.get_delivery_by_order(order)
        print(time_since_order)

        # Step 1: After 5 minutes, change from "Processing" to "Your Order is being prepared"
        if order.status == 'Processing' and time_since_order > timedelta(minutes=5):
            order.status = 'Your Order is being prepared'
            print(order.status)

        # Step 2: After 15 minutes (total 20 mins), change from "Your Order is being prepared" to "Out for Delivery"
        elif order.status == 'Your Order is being prepared' and time_since_order > timedelta(minutes=20):
            order.status = 'Out for Delivery'
            delivery.estimated_delivery_time = now + timedelta(minutes=30)  # Update estimated delivery time

        # Step 3: Change to "Delivered" once the estimated delivery time is reached
        elif order.status == 'Out for Delivery' and now >= delivery.estimated_delivery_time:
            self.deliveryPersonService.delivery_done(delivery.delivery_person)  # Call the method to handle order delivery
            order.status = 'Delivered'

        self.orderRepository.update_order(order)

    def cancel_order(self, order):
        print("Cancelling order")
        for item in order.items.all():
            if item.pizza:
                if order.customer.count_pizza < item.quantity:
                    order.customer.count_pizza += (10 - item.quantity)
                else:
                    order.customer.count_pizza -= item.quantity
        self.customerService.update_customer(order.customer)
        order.status = 'Cancelled'
        delivery = self.deliveryService.get_delivery_by_order(order)
        delivery_person = delivery.delivery_person
        self.deliveryPersonService.delivery_done(delivery_person)
        self.orderRepository.update_order(order)
        return order
    

    def apply_BD_gift(self, order):
        customer = order.customer
        if self.customerService.is_birthday_today(customer):

            pizzas = self.orderItemService.get_pizzas(order)
            cheapest_pizza = min(pizzas, key=lambda x:self.menuService.calculate_price(x.pizza)) if pizzas else None

            if cheapest_pizza:
                self.getFreePizza(order, cheapest_pizza)
                customer.last_BD_gift = datetime.now().date()
                
            drinks = self.orderItemService.get_drinks(order)
            cheapest_drink = min(drinks, key=lambda x: x.drink.price) if drinks else None

            if cheapest_drink:
                self.getFreeDrink(order, cheapest_drink)
                customer.last_BD_gift = datetime.now().date()

            self.orderRepository.update_order(order)
            self.customerService.update_customer(customer)



    def loyaltyDiscount(self, order, eligible_for_loyalty_discount):
        customer = order.customer

        if eligible_for_loyalty_discount:
            order.price *= Decimal(0.9)
            customer.count_pizza %= 10
            self.orderRepository.update_order(order)
            self.customerService.update_customer(customer)



