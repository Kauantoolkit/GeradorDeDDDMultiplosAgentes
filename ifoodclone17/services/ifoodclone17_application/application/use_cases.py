"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio ifoodclone17_application.
"""

from uuid import UUID
from domain.ifoodclone17_application_entities import Orderservice


class CreateOrderserviceUseCase:
    """Use case para criar Orderservice."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Orderservice:
        entity = Orderservice.create(**data)
        return await self.repository.save(entity)


class GetOrderserviceByIdUseCase:
    """Use case para buscar Orderservice por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Orderservice | None:
        return await self.repository.get_by_id(id)


class UpdateOrderserviceUseCase:
    """Use case para atualizar Orderservice."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> Orderservice | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteOrderserviceUseCase:
    """Use case para deletar Orderservice."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
