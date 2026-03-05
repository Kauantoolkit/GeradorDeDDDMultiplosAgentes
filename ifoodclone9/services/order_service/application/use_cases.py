from services.order_service.domain import Order
from pydantic import BaseModel
class CreateOrderUseCase:
    def __init__(self, order: Order):
        self.order = order
    def execute(self):
        # Criação do pedido
        order.save()
        return order
