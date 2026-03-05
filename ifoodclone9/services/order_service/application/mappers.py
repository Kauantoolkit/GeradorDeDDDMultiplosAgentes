from services.order_service.application.dtos import OrderDto
from services.order_service.domain import Order
def map_order(order: Order) -> OrderDto:
    return OrderDto(id=order.id, product_id=order.product_id, quantity=order.quantity)
