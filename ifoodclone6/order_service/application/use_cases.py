from .dtos import OrderDTO
from ..domain import OrderAggregate
from ..domain.events import OrderCreatedEvent

class CreateOrderUseCase:
    def __init__(self, order_repository):
        self.order_repository = order_repository

    def execute(self, order_dto: OrderDTO):
        order = OrderAggregate(OrderId(order_dto.order_id), order_dto.customer_id, order_dto.items)
        self.order_repository.save(order)
        self.order_repository.publish_event(OrderCreatedEvent(order_dto.order_id, order_dto.customer_id, order_dto.items))

class GetOrderUseCase:
    def __init__(self, order_repository):
        self.order_repository = order_repository

    def execute(self, order_id: str):
        return self.order_repository.get(OrderId(order_id))