from datetime import datetime
from app.customers.customerRepository import CustomerRepository


class CustomerService:
    def __init__(self):
        self.customerRepository = CustomerRepository()

    def get_customer_by_user(self, user):
        return self.customerRepository.get_customer_by_user(user)

    def update_customer(self, customer):
        return self.customerRepository.update_customer(customer)
    
    def get_all_customers(self):
        return self.customerRepository.get_all_customers()
    
    def is_eligible_for_discount(self, customer):
        return customer.count_pizza >= 10

    def is_birthday_today(self, customer):
        print(customer.last_BD_gift != datetime.now().date())
        print(customer.birthday == datetime.now().strftime('%m-%d'))
        # compare the dates without year
        return customer.birthday.strftime('%m-%d') == datetime.now().strftime('%m-%d') and (customer.last_BD_gift is None or customer.last_BD_gift != datetime.now().date())