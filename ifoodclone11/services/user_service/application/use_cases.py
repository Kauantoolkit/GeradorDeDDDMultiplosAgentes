"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio users.
"""

from uuid import UUID
from domain.users_entities import User


class CreateUserUseCase:
    """Use case para criar User."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> User:
        entity = User.create(**data)
        return await self.repository.save(entity)


class GetUserByIdUseCase:
    """Use case para buscar User por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> User | None:
        return await self.repository.get_by_id(id)


class UpdateUserUseCase:
    """Use case para atualizar User."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> User | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteUserUseCase:
    """Use case para deletar User."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
