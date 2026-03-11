"""Use cases for academia."""
from uuid import UUID
from domain.academia_entities import User

class CreateUserUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> User:
        entity = User.create(**data)
        return await self.repository.save(entity)

class GetUserByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> User | None:
        return await self.repository.get_by_id(id)
