from app.Menu.repositories.ingredientsRepository import IngredientsRepository


class IngredientsService:
    def __init__(self):
        self.ingredientsRepository = IngredientsRepository()

    def get_all_ingredients(self):
        return self.ingredientsRepository.get_all_ingredients()
    
    def get_ingredient_price(self, ingredient):
        return self.ingredientsRepository.get_ingredient_price(ingredient)
    
    def get_ingredient_by_name(self, ingredient_name):
        return self.ingredientsRepository.get_ingredient_by_name(ingredient_name)