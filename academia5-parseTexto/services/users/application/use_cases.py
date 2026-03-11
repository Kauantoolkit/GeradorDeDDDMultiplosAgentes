"""Use cases for users."""
from uuid import UUID
from domain.users_entities import Entity

class CreateEntityUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Entity:
        entity = Entity.create(**data)
        return await self.repository.save(entity)

class GetEntityByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Entity | None:
        return await self.repository.get_by_id(id)
