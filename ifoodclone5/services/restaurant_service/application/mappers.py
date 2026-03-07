"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import RestaurantDTO, CreateRestaurantDTO
from domain.restaurant_entities import Restaurant


class RestaurantMapper:
    """Mapper para Restaurant."""
    
    @staticmethod
    def to_dto(entity: Restaurant) -> RestaurantDTO:
        return RestaurantDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: RestaurantDTO) -> Restaurant:
        return Restaurant(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateRestaurantDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
