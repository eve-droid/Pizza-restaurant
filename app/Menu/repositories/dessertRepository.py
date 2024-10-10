from app.Menu.models import Dessert

class DessertRepository:
    def __init__(self):
        self = self

    def get_all_desserts(self):
        return Dessert.objects.all()
    
    def get_dessert_by_id(self, dessert_id):
        return Dessert.objects.get(id=dessert_id)