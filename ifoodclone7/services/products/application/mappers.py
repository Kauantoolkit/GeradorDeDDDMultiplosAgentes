"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import ProductDTO, CreateProductDTO
from domain.product import Product


class ProductMapper:
    """Mapper para Product."""
    
    @staticmethod
    def to_dto(entity: Product) -> ProductDTO:
        return ProductDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: ProductDTO) -> Product:
        return Product(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateProductDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
