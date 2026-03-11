"""Use cases for instructor."""
from uuid import UUID
from domain.instructor_entities import Instructor

class CreateInstructorUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Instructor:
        entity = Instructor.create(**data)
        return await self.repository.save(entity)

class GetInstructorByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Instructor | None:
        return await self.repository.get_by_id(id)
