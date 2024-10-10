from app.customers.models import Customer


class CustomerRepository:
    def __init__(self):
        self = self

    def get_customer_by_user(self, user):
        return Customer.objects.get(user=user)

    def update_customer(self, customer):
        return customer.save()
    
    def get_all_customers(self):
        return Customer.objects.all()
    
    def save(self):
        return self.save()