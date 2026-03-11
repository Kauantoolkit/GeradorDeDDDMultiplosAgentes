"""Use cases for course."""
from uuid import UUID
from domain.course_entities import Course

class CreateCourseUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Course:
        entity = Course.create(**data)
        return await self.repository.save(entity)

class GetCourseByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Course | None:
        return await self.repository.get_by_id(id)
