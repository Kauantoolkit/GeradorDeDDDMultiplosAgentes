"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import OrderDTO, CreateOrderDTO
from domain.order_entities import Order


class OrderMapper:
    """Mapper para Order."""
    
    @staticmethod
    def to_dto(entity: Order) -> OrderDTO:
        return OrderDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: OrderDTO) -> Order:
        return Order(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateOrderDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
