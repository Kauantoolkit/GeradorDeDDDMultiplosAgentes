"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import DeliveryDTO, CreateDeliveryDTO
from domain.delivery_entities import Delivery


class DeliveryMapper:
    """Mapper para Delivery."""
    
    @staticmethod
    def to_dto(entity: Delivery) -> DeliveryDTO:
        return DeliveryDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: DeliveryDTO) -> Delivery:
        return Delivery(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateDeliveryDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
