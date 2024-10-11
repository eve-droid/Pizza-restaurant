from decimal import ROUND_UP, Decimal
from app.Menu.repositories.dessertRepository import DessertRepository
from app.Menu.repositories.drinkRepository import DrinkRepository
from app.Menu.repositories.pizzaRepository import PizzaRepository
from app.Menu.services.ingredientsService import IngredientsService


class MenuService:
    def __init__(self):
        self.pizzaRepository = PizzaRepository()
        self.drinkRepository = DrinkRepository()
        self.dessertRepository = DessertRepository()
        self.ingredients_service = IngredientsService()

    def get_pizza_by_id(self, id):
        return self.pizzaRepository.get_pizza_by_id(id)
    
    def get_drink_by_id(self, drink_id):
        return self.drinkRepository.get_drink_by_id(drink_id)
    
    def get_dessert_by_id(self, dessert_id):   
        return self.dessertRepository.get_dessert_by_id(dessert_id)

    def get_all_pizzas(self):
        return self.pizzaRepository.get_all_pizzas()
    
    def get_all_drinks(self):
        return self.drinkRepository.get_all_drinks()
    
    def get_all_desserts(self):
        return self.dessertRepository.get_all_desserts()
    
    
    def calculate_price(self, pizza):
        #calculate price of a pizza based on its ingredients
        pizza.price = Decimal(0.2)  #price of flour for pizza base

        for ingredient in self.pizzaRepository.get_pizza_ingredients(pizza):
            pizza.price += self.ingredients_service.get_ingredient_price(ingredient)

        pizza.price += (pizza.price * Decimal(0.4))
        pizza.price += (pizza.price * Decimal(0.09))
        pizza.price = pizza.price.quantize(Decimal('1'), rounding=ROUND_UP) - Decimal(0.01)
        pizza.price = pizza.price.quantize(Decimal('0.01'), rounding=ROUND_UP)
        return pizza.price
    

    def check_if_vegetarian(self, pizza):
        #check if pizza is vegetarien
        for ingredient_name in self.pizzaRepository.get_pizza_ingredients(pizza):
            ingredient = self.ingredients_service.get_ingredient_by_name(ingredient_name)
            if ingredient.vegetarian == False:
                return False
        return True
    
    def get_pizza_ingredients(self, pizza):
        return self.pizzaRepository.get_pizza_ingredients(pizza)
    
