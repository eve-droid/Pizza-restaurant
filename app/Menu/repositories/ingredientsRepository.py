from app.Menu.models import All_Ingredients

class IngredientsRepository:
    def __init__(self):
        self = self

    def get_all_ingredients(self):
        return All_Ingredients.objects.all()
    
    def get_ingredient_price(self, ingredient):
        return All_Ingredients.objects.get(name=ingredient).price
    
    def get_ingredient_by_name(self, ingredient_name):
        return All_Ingredients.objects.get(name=ingredient_name)