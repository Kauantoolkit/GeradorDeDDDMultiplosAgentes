from .dtos import OrderDTO
from ..domain import OrderAggregate

class OrderMapper:
    @staticmethod
    def to_dto(order: OrderAggregate) -> OrderDTO:
        return OrderDTO(order.order_id.value, order.customer_id, [item.product_id for item in order.items])