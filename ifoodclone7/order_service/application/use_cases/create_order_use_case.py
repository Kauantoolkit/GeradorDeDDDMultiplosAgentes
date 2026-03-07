from domain.entities import Order

class CreateOrderUseCase:
    def __init__(self, order_repository):
        self.order_repository = order_repository

    def execute(self, order: Order):
        self.order_repository.save(order)
