"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio delivery.
"""

from uuid import UUID
from domain.delivery_entities import Delivery


class CreateDeliveryUseCase:
    """Use case para criar Delivery."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Delivery:
        entity = Delivery.create(**data)
        return await self.repository.save(entity)


class GetDeliveryByIdUseCase:
    """Use case para buscar Delivery por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Delivery | None:
        return await self.repository.get_by_id(id)


class UpdateDeliveryUseCase:
    """Use case para atualizar Delivery."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> Delivery | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteDeliveryUseCase:
    """Use case para deletar Delivery."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
