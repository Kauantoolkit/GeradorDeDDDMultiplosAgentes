"""Mappers for classes."""
from application.dtos import ClassDTO
from domain.classes_entities import Class

class ClassMapper:
    @staticmethod
    def to_dto(entity: Class) -> ClassDTO:
        return ClassDTO(id=entity.id)
