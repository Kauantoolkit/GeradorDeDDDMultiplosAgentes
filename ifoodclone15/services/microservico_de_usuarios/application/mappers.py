"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import UsuariosEntityDTO, CreateUsuariosEntityDTO
from domain.usuarios_entities import UsuariosEntity


class UsuariosEntityMapper:
    """Mapper para UsuariosEntity."""
    
    @staticmethod
    def to_dto(entity: UsuariosEntity) -> UsuariosEntityDTO:
        return UsuariosEntityDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: UsuariosEntityDTO) -> UsuariosEntity:
        return UsuariosEntity(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateUsuariosEntityDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
