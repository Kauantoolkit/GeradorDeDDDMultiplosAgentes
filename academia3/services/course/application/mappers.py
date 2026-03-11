"""Mappers for course."""
from application.dtos import CourseDTO
from domain.course_entities import Course

class CourseMapper:
    @staticmethod
    def to_dto(entity: Course) -> CourseDTO:
        return CourseDTO(id=entity.id)
