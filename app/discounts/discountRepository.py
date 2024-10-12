from app.discounts.models import Discount


class DiscountRepository:
    def __init__(self):
        self = self

    def get_discount_by_code(self, code):
        return Discount.objects.get(discount_code=code)

    def save(self, order):
        return order.save()