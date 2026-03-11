"""Mappers for lesson."""
from application.dtos import LessonDTO
from domain.lesson_entities import Lesson

class LessonMapper:
    @staticmethod
    def to_dto(entity: Lesson) -> LessonDTO:
        return LessonDTO(id=entity.id)
