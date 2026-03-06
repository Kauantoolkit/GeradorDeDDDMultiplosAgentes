"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import AddressDTO, CreateAddressDTO
from domain.shipping_entities import Address


class AddressMapper:
    """Mapper para Address."""
    
    @staticmethod
    def to_dto(entity: Address) -> AddressDTO:
        return AddressDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: AddressDTO) -> Address:
        return Address(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateAddressDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
