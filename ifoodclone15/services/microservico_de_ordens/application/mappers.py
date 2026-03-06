"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import OrdensEntityDTO, CreateOrdensEntityDTO
from domain.ordens_entities import OrdensEntity


class OrdensEntityMapper:
    """Mapper para OrdensEntity."""
    
    @staticmethod
    def to_dto(entity: OrdensEntity) -> OrdensEntityDTO:
        return OrdensEntityDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: OrdensEntityDTO) -> OrdensEntity:
        return OrdensEntity(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateOrdensEntityDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
