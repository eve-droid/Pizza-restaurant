from app.Menu.models import Pizza

class PizzaRepository:
    def __init__(self):
        self = self

    def get_all_pizzas(self):
        return Pizza.objects.all()
    
    def get_pizza_by_id(self, pizza_id):
        return Pizza.objects.get(id=pizza_id)
    
    def get_pizza_ingredients(self, pizza):
        return pizza.ingredients.split(', ')

    