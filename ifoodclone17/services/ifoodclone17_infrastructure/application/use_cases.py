"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio ifoodclone17_infrastructure.
"""

from uuid import UUID
from domain.ifoodclone17_infrastructure_entities import Database


class CreateDatabaseUseCase:
    """Use case para criar Database."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Database:
        entity = Database.create(**data)
        return await self.repository.save(entity)


class GetDatabaseByIdUseCase:
    """Use case para buscar Database por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Database | None:
        return await self.repository.get_by_id(id)


class UpdateDatabaseUseCase:
    """Use case para atualizar Database."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> Database | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteDatabaseUseCase:
    """Use case para deletar Database."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
