"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import ProdutosEntityDTO, CreateProdutosEntityDTO
from domain.produtos_entities import ProdutosEntity


class ProdutosEntityMapper:
    """Mapper para ProdutosEntity."""
    
    @staticmethod
    def to_dto(entity: ProdutosEntity) -> ProdutosEntityDTO:
        return ProdutosEntityDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: ProdutosEntityDTO) -> ProdutosEntity:
        return ProdutosEntity(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateProdutosEntityDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
