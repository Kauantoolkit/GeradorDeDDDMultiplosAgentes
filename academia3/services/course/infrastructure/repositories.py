"""Repositories for course."""
from uuid import UUID
from typing import Optional
from domain.course_entities import Course, CourseRepository

class CourseRepositoryImpl(CourseRepository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[Course]:
        pass
    
    async def get_all(self) -> list[Course]:
        pass
    
    async def save(self, entity: Course) -> Course:
        return entity

_repository_instance = None

def get_course_repository() -> CourseRepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = CourseRepositoryImpl()
    return _repository_instance
