from django import template
from app.orders.models import Pizza

register = template.Library()

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
def calculate_price(pizza_id):
    # Fetch pizza price by pizza_id
    try:
        pizza = Pizza.objects.get(id=pizza_id)
        return pizza.calculate_price()
    except Pizza.DoesNotExist:
        return 'N/A'
    
@register.filter
def get_ingredients(pizza_id):
    # Get the pizza object using the provided ID
    try:
        pizza = Pizza.objects.get(id=pizza_id)
        return pizza.get_ingredients()
    except Pizza.DoesNotExist:
        return []