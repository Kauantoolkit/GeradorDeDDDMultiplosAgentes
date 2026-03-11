"""Mappers for enrollments."""
from application.dtos import EntityDTO
from domain.enrollments_entities import Entity

class EntityMapper:
    @staticmethod
    def to_dto(entity: Entity) -> EntityDTO:
        return EntityDTO(id=entity.id)
