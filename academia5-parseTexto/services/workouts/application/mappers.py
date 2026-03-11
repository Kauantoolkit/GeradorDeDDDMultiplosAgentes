"""Mappers for workouts."""
from application.dtos import EntityDTO
from domain.workouts_entities import Entity

class EntityMapper:
    @staticmethod
    def to_dto(entity: Entity) -> EntityDTO:
        return EntityDTO(id=entity.id)
