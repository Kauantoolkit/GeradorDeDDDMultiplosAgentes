"""
Order Service - Application Layer
====================================
Use cases, DTOs, and mappers for order service.
"""

# DTOs
from .dtos import (
    CreateOrderDTO,
    UpdateOrderDTO,
    OrderDTO,
    OrderItemDTO,
    OrderListDTO,
    CancelOrderDTO,
    OrderStatusDTO,
    order_to_dto,
    dto_to_create_order_dict
)

# Mappers
from .mappers import (
    OrderMapper,
    OrderItemMapper,
    OrderAggregateMapper,
    map_create_dto_to_dict,
    map_entity_to_dict,
    map_entities_to_list
)

__all__ = [
    # DTOs
    "CreateOrderDTO",
    "UpdateOrderDTO",
    "OrderDTO",
    "OrderItemDTO",
    "OrderListDTO",
    "CancelOrderDTO",
    "OrderStatusDTO",
    "order_to_dto",
    "dto_to_create_order_dict",
    # Mappers
    "OrderMapper",
    "OrderItemMapper",
    "OrderAggregateMapper",
    "map_create_dto_to_dict",
    "map_entity_to_dict",
    "map_entities_to_list"
]

