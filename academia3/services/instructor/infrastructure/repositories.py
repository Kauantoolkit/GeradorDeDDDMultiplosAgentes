"""Repositories for instructor."""
from uuid import UUID
from typing import Optional
from domain.instructor_entities import Instructor, InstructorRepository

class InstructorRepositoryImpl(InstructorRepository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[Instructor]:
        pass
    
    async def get_all(self) -> list[Instructor]:
        pass
    
    async def save(self, entity: Instructor) -> Instructor:
        return entity

_repository_instance = None

def get_instructor_repository() -> InstructorRepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = InstructorRepositoryImpl()
    return _repository_instance
