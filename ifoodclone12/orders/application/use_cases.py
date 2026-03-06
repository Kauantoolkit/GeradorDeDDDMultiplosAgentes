from orders.domain.entities import Order
class CreateOrderUseCase:
    def __init__(self, order: Order):
        self.order = order
    def execute(self):
        # logic to create order
        pass
