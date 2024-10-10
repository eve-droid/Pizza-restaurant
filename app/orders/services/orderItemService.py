from app.Menu.services.menuService import MenuService
from app.customers.customerService import CustomerService
from app.orders.repositories.orderItemRepository import OrderItemRepository
from unitOfWork import UnitOfWork


class OrderItemService:
    def __init__(self):
        self.orderItemRepository = OrderItemRepository()
        self.unitOfWork = UnitOfWork()
        self.menuService = MenuService()
        self.customerService = CustomerService()

    def populate_order_items(self, customer, quantities, order):

        self.unitOfWork.orders.add(order)

        for key in quantities.keys():
            if key.startswith('pizzaQuantities['):
                pizza_id = key.split('[')[1][:-1]
                quantity = int(quantities[key])
                if quantity > 0:
                    pizza = self.menuService.get_pizza_by_id(pizza_id) #get the pizza object
                    order_item = self.orderItemRepository.create_order_item(order=order, pizza=pizza, quantity=quantity) #create order item object
                    self.unitOfWork.order_items.add(order_item) #add it to the dirty list
                    customer.count_pizza += quantity

            elif key.startswith('drinkQuantities['):
                drink_id = key.split('[')[1][:-1]
                quantity = int(quantities[key])
                if quantity > 0:
                    drink = self.menuService.get_drink_by_id(drink_id)
                    order_item = self.orderItemRepository.create_order_item(order=order, drink=drink, quantity=quantity) #create order item object
                    self.unitOfWork.order_items.add(order_item)

            elif key.startswith('dessertQuantities['):
                dessert_id = key.split('[')[1][:-1]
                quantity = int(quantities[key])
                if quantity > 0:
                    dessert = self.menuService.get_dessert_by_id(dessert_id)
                    order_item = self.orderItemRepository.create_order_item(order=order, dessert=dessert, quantity=quantity) #create order item object
                    self.unitOfWork.order_items.add(order_item)

        self.customerService.update_customer(customer)

        self.unitOfWork.commit()

    def get_pizzas(self, order):
        return self.orderItemRepository.get_pizzas(order)
    
    def get_drinks(self, order):    
        return self.orderItemRepository.get_drinks(order)
    
    def get_desserts(self, order):
        return self.orderItemRepository.get_desserts(order)
    
    def get_order_items(self, order):
        return self.orderItemRepository.get_order_items(order)