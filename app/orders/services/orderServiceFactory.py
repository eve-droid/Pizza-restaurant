#the orderSercive class has a lot of dependencies/repositories, 
# to avoid needing to create instances of those dependendies everytime we want to create an instance of the orderService class,
#we use the orderServiceFactory class to create an instance of the orderService class with all the dependencies already injected

from app.Menu.services.menuService import MenuService
from app.customers.customerService import CustomerService
from app.delivery.services.deliveryPersonService import DeliveryPersonService
from app.delivery.services.deliveryService import DeliveryService
from app.discounts.discountService import DiscountService
from app.orders.services.orderItemService import OrderItemService
from app.orders.services.orderService import OrderService
from app.orders.repositories.orderRepository import OrderRepository

class ServiceFactory:
    def __init__(self):
        # Initialize all services and repositories here
        self.customer_service = CustomerService()
        self.menu_service = MenuService()
        self.discount_service = DiscountService()
        self.delivery_service = DeliveryService()
        self.deliveryPerson_service = DeliveryPersonService()
        self.orderItem_service = OrderItemService()
        self.order_repository = OrderRepository()

    def create_order_service(self):
        return OrderService(
            customerService=self.customer_service,
            menuService=self.menu_service,
            discountService=self.discount_service,
            deliveryService=self.delivery_service,
            deliveryPersonService=self.deliveryPerson_service,
            orderItemService=self.orderItem_service,
            orderRepository=self.order_repository
        )