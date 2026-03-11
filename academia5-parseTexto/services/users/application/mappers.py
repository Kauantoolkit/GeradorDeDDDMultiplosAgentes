"""Mappers for users."""
from application.dtos import EntityDTO
from domain.users_entities import Entity

class EntityMapper:
    @staticmethod
    def to_dto(entity: Entity) -> EntityDTO:
        return EntityDTO(id=entity.id)
