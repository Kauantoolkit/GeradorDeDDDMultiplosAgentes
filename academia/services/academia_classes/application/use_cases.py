"""Use cases for classes."""
from uuid import UUID
from domain.classes_entities import Class

class CreateClassUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Class:
        entity = Class.create(**data)
        return await self.repository.save(entity)

class GetClassByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Class | None:
        return await self.repository.get_by_id(id)
