from app.Menu.models import Drink

class DrinkRepository:
    def __init__(self):
        self = self

    def get_all_drinks(self):
        return Drink.objects.all()
    
    def get_drink_by_id(self, drink_id):
        return Drink.objects.get(id=drink_id)