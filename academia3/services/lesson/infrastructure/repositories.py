"""Repositories for lesson."""
from uuid import UUID
from typing import Optional
from domain.lesson_entities import Lesson, LessonRepository

class LessonRepositoryImpl(LessonRepository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[Lesson]:
        pass
    
    async def get_all(self) -> list[Lesson]:
        pass
    
    async def save(self, entity: Lesson) -> Lesson:
        return entity

_repository_instance = None

def get_lesson_repository() -> LessonRepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = LessonRepositoryImpl()
    return _repository_instance
