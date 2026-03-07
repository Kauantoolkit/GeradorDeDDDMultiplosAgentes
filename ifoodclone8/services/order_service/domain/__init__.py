"""
Order Service - Domain Layer
================================
Domain entities, value objects, and aggregates for order service.
"""

# Entities
from .order_entities import Order, OrderItem, OrderRepository, OrderItemRepository

# Value Objects
from .order_value_objects import (
    OrderId,
    CustomerId, 
    ProductId,
    Address,
    Email,
    Money,
    OrderStatus,
    PhoneNumber
)

# Aggregates
from .order_aggregates import OrderAggregate, OrderFactory

__all__ = [
    # Entities
    "Order",
    "OrderItem",
    "OrderRepository",
    "OrderItemRepository",
    # Value Objects
    "OrderId",
    "CustomerId",
    "ProductId",
    "Address",
    "Email",
    "Money",
    "OrderStatus",
    "PhoneNumber",
    # Aggregates
    "OrderAggregate",
    "OrderFactory"
]

