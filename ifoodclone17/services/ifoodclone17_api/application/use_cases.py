"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio ifoodclone17_api.
"""

from uuid import UUID
from domain.ifoodclone17_api_entities import Ordercontroller


class CreateOrdercontrollerUseCase:
    """Use case para criar Ordercontroller."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Ordercontroller:
        entity = Ordercontroller.create(**data)
        return await self.repository.save(entity)


class GetOrdercontrollerByIdUseCase:
    """Use case para buscar Ordercontroller por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Ordercontroller | None:
        return await self.repository.get_by_id(id)


class UpdateOrdercontrollerUseCase:
    """Use case para atualizar Ordercontroller."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> Ordercontroller | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteOrdercontrollerUseCase:
    """Use case para deletar Ordercontroller."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
