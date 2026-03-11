"""Mappers for instructor."""
from application.dtos import InstructorDTO
from domain.instructor_entities import Instructor

class InstructorMapper:
    @staticmethod
    def to_dto(entity: Instructor) -> InstructorDTO:
        return InstructorDTO(id=entity.id)
