"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import DatabaseDTO, CreateDatabaseDTO
from domain.ifoodclone17_infrastructure_entities import Database


class DatabaseMapper:
    """Mapper para Database."""
    
    @staticmethod
    def to_dto(entity: Database) -> DatabaseDTO:
        return DatabaseDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: DatabaseDTO) -> Database:
        return Database(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateDatabaseDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
