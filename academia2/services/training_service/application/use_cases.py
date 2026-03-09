"""Use cases for training."""
from uuid import UUID
from domain.training_entities import Session

class CreateSessionUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Session:
        entity = Session.create(**data)
        return await self.repository.save(entity)

class GetSessionByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Session | None:
        return await self.repository.get_by_id(id)
