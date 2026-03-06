"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import PedidosEntityDTO, CreatePedidosEntityDTO
from domain.pedidos_entities import PedidosEntity


class PedidosEntityMapper:
    """Mapper para PedidosEntity."""
    
    @staticmethod
    def to_dto(entity: PedidosEntity) -> PedidosEntityDTO:
        return PedidosEntityDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: PedidosEntityDTO) -> PedidosEntity:
        return PedidosEntity(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreatePedidosEntityDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
