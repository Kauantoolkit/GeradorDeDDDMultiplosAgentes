"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio ordens.
"""

from uuid import UUID
from domain.ordens_entities import OrdensEntity


class CreateOrdensEntityUseCase:
    """Use case para criar OrdensEntity."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> OrdensEntity:
        entity = OrdensEntity.create(**data)
        return await self.repository.save(entity)


class GetOrdensEntityByIdUseCase:
    """Use case para buscar OrdensEntity por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> OrdensEntity | None:
        return await self.repository.get_by_id(id)


class UpdateOrdensEntityUseCase:
    """Use case para atualizar OrdensEntity."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> OrdensEntity | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteOrdensEntityUseCase:
    """Use case para deletar OrdensEntity."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
