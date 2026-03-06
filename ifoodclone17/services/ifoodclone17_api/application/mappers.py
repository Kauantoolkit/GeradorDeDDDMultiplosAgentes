"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import OrdercontrollerDTO, CreateOrdercontrollerDTO
from domain.ifoodclone17_api_entities import Ordercontroller


class OrdercontrollerMapper:
    """Mapper para Ordercontroller."""
    
    @staticmethod
    def to_dto(entity: Ordercontroller) -> OrdercontrollerDTO:
        return OrdercontrollerDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: OrdercontrollerDTO) -> Ordercontroller:
        return Ordercontroller(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateOrdercontrollerDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
