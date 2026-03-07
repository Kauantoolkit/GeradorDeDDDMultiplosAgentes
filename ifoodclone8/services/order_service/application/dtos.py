"""
DTOs - Application Layer
========================
Data Transfer Objects para o domínio order.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass
class CreateOrderDTO:
    """DTO para criação de um novo pedido."""
    customer_id: str
    items: List[dict]
    delivery_address: Optional[dict] = None
    notes: Optional[str] = None


@dataclass
class UpdateOrderDTO:
    """DTO para atualização de um pedido."""
    order_id: str
    status: Optional[str] = None
    items: Optional[List[dict]] = None
    delivery_address: Optional[dict] = None
    notes: Optional[str] = None


@dataclass
class OrderDTO:
    """DTO para representação de um pedido."""
    id: str
    customer_id: str
    items: List[dict]
    status: str
    total: float
    delivery_address: Optional[dict] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Converte o DTO para dicionário."""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "items": self.items,
            "status": self.status,
            "total": self.total,
            "delivery_address": self.delivery_address,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class OrderItemDTO:
    """DTO para representação de um item de pedido."""
    id: str
    order_id: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    subtotal: float
    
    def to_dict(self) -> dict:
        """Converte o DTO para dicionário."""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "subtotal": self.subtotal
        }


@dataclass
class OrderListDTO:
    """DTO para lista de pedidos."""
    orders: List[OrderDTO]
    total_count: int
    page: int
    page_size: int


@dataclass
class CancelOrderDTO:
    """DTO para cancelamento de pedido."""
    order_id: str
    reason: Optional[str] = None


@dataclass
class OrderStatusDTO:
    """DTO para atualização de status de pedido."""
    order_id: str
    status: str
    notes: Optional[str] = None


# Funções auxiliares de conversão

def order_to_dto(order) -> OrderDTO:
    """Converte entidade Order para OrderDTO."""
    return OrderDTO(
        id=str(order.id),
        customer_id=order.customer_id,
        items=order.items,
        status=order.status,
        total=order.total,
        created_at=order.created_at,
        updated_at=order.updated_at
    )


def dto_to_create_order_dict(dto: CreateOrderDTO) -> dict:
    """Converte CreateOrderDTO para dicionário."""
    return {
        "customer_id": dto.customer_id,
        "items": dto.items,
        "delivery_address": dto.delivery_address,
        "notes": dto.notes
    }

