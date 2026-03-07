"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from typing import List
from domain.order_entities import Order, OrderItem
from domain.order_aggregates import OrderAggregate
from .dtos import (
    OrderDTO,
    OrderItemDTO,
    CreateOrderDTO,
    UpdateOrderDTO,
    OrderListDTO,
    order_to_dto,
    dto_to_create_order_dict
)


class OrderMapper:
    """Mapper para Order."""
    
    @staticmethod
    def to_dto(entity: Order) -> OrderDTO:
        """Converte entidade Order para OrderDTO."""
        return OrderDTO(
            id=str(entity.id),
            customer_id=entity.customer_id,
            items=entity.items,
            status=entity.status,
            total=entity.total,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    @staticmethod
    def to_entity(dto: OrderDTO) -> Order:
        """Converte OrderDTO para entidade Order."""
        from uuid import UUID
        from datetime import datetime
        
        return Order(
            id=UUID(dto.id),
            customer_id=dto.customer_id,
            items=dto.items,
            status=dto.status,
            total=dto.total,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )
    
    @staticmethod
    def to_dict(dto: OrderDTO) -> dict:
        """Converte OrderDTO para dicionário."""
        return {
            "id": dto.id,
            "customer_id": dto.customer_id,
            "items": dto.items,
            "status": dto.status,
            "total": dto.total,
            "delivery_address": dto.delivery_address,
            "notes": dto.notes,
            "created_at": dto.created_at.isoformat() if dto.created_at else None,
            "updated_at": dto.updated_at.isoformat() if dto.updated_at else None
        }
    
    @staticmethod
    def from_create_dict(data: dict) -> CreateOrderDTO:
        """Converte dicionário para CreateOrderDTO."""
        return CreateOrderDTO(
            customer_id=data.get("customer_id", ""),
            items=data.get("items", []),
            delivery_address=data.get("delivery_address"),
            notes=data.get("notes")
        )


class OrderItemMapper:
    """Mapper para OrderItem."""
    
    @staticmethod
    def to_dto(entity: OrderItem) -> OrderItemDTO:
        """Converte entidade OrderItem para OrderItemDTO."""
        return OrderItemDTO(
            id=str(entity.id),
            order_id=str(entity.order_id),
            product_id=entity.product_id,
            product_name=entity.product_name,
            quantity=entity.quantity,
            unit_price=entity.unit_price,
            subtotal=entity.get_subtotal()
        )
    
    @staticmethod
    def to_entity(dto: OrderItemDTO) -> OrderItem:
        """Converte OrderItemDTO para entidade OrderItem."""
        from uuid import UUID
        from datetime import datetime
        
        return OrderItem(
            id=UUID(dto.id),
            order_id=UUID(dto.order_id),
            product_id=dto.product_id,
            product_name=dto.product_name,
            quantity=dto.quantity,
            unit_price=dto.unit_price,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )


class OrderAggregateMapper:
    """Mapper para OrderAggregate."""
    
    @staticmethod
    def to_dto(aggregate: OrderAggregate) -> dict:
        """Converte OrderAggregate para dicionário com informações completas."""
        return {
            "order": OrderMapper.to_dto(aggregate.root).to_dict(),
            "items": [OrderItemMapper.to_dto(item).to_dict() for item in aggregate.items],
            "total": aggregate.calculate_total(),
            "can_cancel": aggregate.can_cancel()
        }
    
    @staticmethod
    def to_order_dto(aggregate: OrderAggregate) -> OrderDTO:
        """Converte OrderAggregate para OrderDTO."""
        return OrderMapper.to_dto(aggregate.root)
    
    @staticmethod
    def to_order_list_dto(aggregates: List[OrderAggregate], page: int = 1, page_size: int = 10) -> OrderListDTO:
        """Converte lista de OrderAggregate para OrderListDTO."""
        orders = [OrderMapper.to_dto(agg.root) for agg in aggregates]
        return OrderListDTO(
            orders=orders,
            total_count=len(orders),
            page=page,
            page_size=page_size
        )


# Funções de conveniência

def map_create_dto_to_dict(dto: CreateOrderDTO) -> dict:
    """Converte CreateOrderDTO para dicionário de criação."""
    return dto_to_create_order_dict(dto)


def map_entity_to_dict(entity: Order) -> dict:
    """Converte entidade Order para dicionário."""
    return OrderMapper.to_dto(entity).to_dict()


def map_entities_to_list(entities: List[Order]) -> List[dict]:
    """Converte lista de entidades Order para lista de dicionários."""
    return [OrderMapper.to_dto(entity).to_dict() for entity in entities]

