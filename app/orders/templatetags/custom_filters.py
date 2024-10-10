from django import template
from app.Menu.services.menuService import MenuService
from app.orders.models import Pizza

register = template.Library()
menu_service = MenuService()

def test_tag():
    print( "Test successful")

@register.filter(name='get_pizza_ingredients')
def get_pizza_ingredients(pizzas, pizza_id):
    # Fetch pizza ingredients by pizza_id
    try:
        return pizzas[int(pizza_id)]['ingredients']
    except (KeyError, IndexError, ValueError):
        return []

@register.filter
def calculate_price(pizza):
    # Fetch pizza price by pizza_id
    try:
        return menu_service.calculate_price(pizza)
    except Pizza.DoesNotExist:
        return 'N/A'
    
@register.filter
def get_ingredients(pizza_id):
    # Get the pizza object using the provided ID
    try:
        pizza = Pizza.objects.get(id=pizza_id)
        return menu_service.get_pizza_ingredients(pizza)
    except Pizza.DoesNotExist:
        return []
    
@register.filter
def check_if_vegetarian(pizza_id):
    # Check if the pizza is vegetarian
    try:
        pizza = Pizza.objects.get(id=pizza_id)
        return menu_service.check_if_vegetarian(pizza)
    except Pizza.DoesNotExist:
        return False