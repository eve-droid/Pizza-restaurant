from datetime import timezone
from app.discounts.discountRepository import DiscountRepository


class DiscountService:
    def __init__ (self):
        self.discountRepository = DiscountRepository()

    def get_discount_by_code(self, code):
        return self.discountRepository.get_discount_by_code(code)
    
    def is_valid(self, order):
        try:
            if order.used:
                return False
            elif order.end_date and self.end_date <= timezone.now() :
                return False
            else:
                return True
        
        except Exception:
            print('does not exist')
            return False
        
    def update_discount(self, order):
        return self.discountRepository.save(order)
        