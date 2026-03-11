"""Use cases for lesson."""
from uuid import UUID
from domain.lesson_entities import Lesson

class CreateLessonUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Lesson:
        entity = Lesson.create(**data)
        return await self.repository.save(entity)

class GetLessonByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Lesson | None:
        return await self.repository.get_by_id(id)
