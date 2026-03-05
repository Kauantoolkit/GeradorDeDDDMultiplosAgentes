"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio orders.
"""

from uuid import UUID
from domain import Order


class CreateOrderUseCase:
    """Use case para criar Order."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Order:
        entity = Order.create(**data)
        return await self.repository.save(entity)


class GetOrderByIdUseCase:
    """Use case para buscar Order por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Order | None:
        return await self.repository.get_by_id(id)


class UpdateOrderUseCase:
    """Use case para atualizar Order."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> Order | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteOrderUseCase:
    """Use case para deletar Order."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
