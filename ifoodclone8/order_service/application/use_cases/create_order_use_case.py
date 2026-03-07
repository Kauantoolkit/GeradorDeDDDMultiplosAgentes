from .dtos import CreateOrderDTO
from ..domain.aggregates import OrderAggregate
from ..domain.value_objects import OrderId, CustomerId, ProductId

class CreateOrderUseCase:
    def __init__(self, order_repository):
        self.order_repository = order_repository

    def execute(self, dto: CreateOrderDTO):
        order_id = OrderId(dto.order_id)
        customer_id = CustomerId(dto.customer_id)
        items = [OrderItem(ProductId(item['product_id']), item['quantity']) for item in dto.items]
        order = OrderAggregate(order_id, customer_id, items)
        self.order_repository.save(order)