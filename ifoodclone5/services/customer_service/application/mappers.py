"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import CustomerDTO, CreateCustomerDTO
from domain.customer_entities import Customer


class CustomerMapper:
    """Mapper para Customer."""
    
    @staticmethod
    def to_dto(entity: Customer) -> CustomerDTO:
        return CustomerDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: CustomerDTO) -> Customer:
        return Customer(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateCustomerDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
