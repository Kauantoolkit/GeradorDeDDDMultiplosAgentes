"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import OrderserviceDTO, CreateOrderserviceDTO
from domain.ifoodclone17_application_entities import Orderservice


class OrderserviceMapper:
    """Mapper para Orderservice."""
    
    @staticmethod
    def to_dto(entity: Orderservice) -> OrderserviceDTO:
        return OrderserviceDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: OrderserviceDTO) -> Orderservice:
        return Orderservice(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateOrderserviceDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
