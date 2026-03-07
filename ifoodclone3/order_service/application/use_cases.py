from domain.entities import Order
from domain.repositories import OrderRepository

class CreateOrderUseCase:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, order_id, customer_id, items):
        order = Order(order_id, customer_id, items)
        self.order_repository.save(order)

class GetOrderUseCase:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    def execute(self, order_id):
        return self.order_repository.get(order_id)