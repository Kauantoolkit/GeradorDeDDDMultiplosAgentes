from .dtos import OrderDTO
from ..domain import OrderAggregate
from ..domain.value_objects import OrderId, CustomerId, ProductId

class OrderMapper:
    @staticmethod
    def to_dto(order: OrderAggregate) -> OrderDTO:
        return OrderDTO(order.order_id.value, order.customer_id.value, [{'product_id': item.product_id.value, 'quantity': item.quantity} for item in order.items])