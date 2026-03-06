from ifoodclone17.domain import Order
from ifoodclone17.application import UseCase
class OrderService(UseCase):
    def get_orders(self):
        return [Order() for _ in range(10)]
    def create_order(self):
        return Order()
