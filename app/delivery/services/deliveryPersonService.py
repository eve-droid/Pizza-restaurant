from datetime import timedelta, timezone
from django.utils import timezone
from app.delivery.repositories.deliveryPersonRepository import DeliveryPersonRepository
from app.delivery.services.deliveryService import DeliveryService


class DeliveryPersonService:
    def __init__(self):
        self.deliveryPersonRepository = DeliveryPersonRepository()
        self.deliveryService = DeliveryService()

    
    def save(self, deliveryPerson):
        return self.deliveryPersonRepository.save(deliveryPerson)
    

    def assign_delivery_person(self, delivery, order):
        postal_code = order.customer.address_postal_code
        print(postal_code)

        #if there is someone with the right postal code, which already has been assigned with max 2 deliveries in the last 3 min, select that delivery person
        delivery_person = self.deliveryPersonRepository.filter_persons_by_postalCode_and_assignedTime(order, postal_code)
        if delivery_person:
            self.set_delivery_person(delivery_person)
            delivery.delivery_person = delivery_person
        else:
            #else select someone who is available and has the correct postal code
            delivery_person = self.deliveryPersonRepository.filter_persons_by_postalCode(postal_code)
            if delivery_person:
                self.set_delivery_person(delivery_person)
                delivery.delivery_person = delivery_person
            else:
                #else select someone who is available and has no postal code assigned
                delivery_person = self.deliveryPersonRepository.filter_persons_by_postalCode(postal_code=None) #assumption, we will always have enough personal for this case
                delivery_person.postal_code_area = postal_code
                self.set_delivery_person(delivery_person)
                delivery.delivery_person = delivery_person
        
        self.deliveryService.save(delivery)
        self.deliveryPersonRepository.save(delivery_person)

    
    def is_available(self, deliveryPerson):
        return (deliveryPerson.available or deliveryPerson.assigned_time+timedelta(minutes=30) <= timezone.now()) & (deliveryPerson.assigned_orders < 3)
    

    def set_delivery_person(self, deliveryPerson):
        if deliveryPerson:  
            print(deliveryPerson.name)
            deliveryPerson.assigned_orders += 1
            deliveryPerson.available = False  # Immediately mark the delivery person unavailable
            if deliveryPerson.assigned_orders == 1: 
                deliveryPerson.assigned_time = timezone.now() #set the assigned time (only if it's the first order)
            self.deliveryPersonRepository.save(deliveryPerson)
        else:
            raise ValueError("No delivery personnel available for this postal code.")
        

    def delivery_done(self, deliveryPerson):
        deliveryPerson.assigned_orders -= 1
        if deliveryPerson.assigned_orders == 0:
            deliveryPerson.available = True  # Make the delivery person available
        self.deliveryPersonRepository.save()