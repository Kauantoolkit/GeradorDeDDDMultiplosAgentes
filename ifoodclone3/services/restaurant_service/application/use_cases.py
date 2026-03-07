"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio restaurant.
"""

from uuid import UUID
from domain.restaurant_entities import Restaurant


class CreateRestaurantUseCase:
    """Use case para criar Restaurant."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Restaurant:
        entity = Restaurant.create(**data)
        return await self.repository.save(entity)


class GetRestaurantByIdUseCase:
    """Use case para buscar Restaurant por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Restaurant | None:
        return await self.repository.get_by_id(id)


class UpdateRestaurantUseCase:
    """Use case para atualizar Restaurant."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> Restaurant | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteRestaurantUseCase:
    """Use case para deletar Restaurant."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
