"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio shipping.
"""

from uuid import UUID
from domain.shipping_entities import Address


class CreateAddressUseCase:
    """Use case para criar Address."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Address:
        entity = Address.create(**data)
        return await self.repository.save(entity)


class GetAddressByIdUseCase:
    """Use case para buscar Address por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Address | None:
        return await self.repository.get_by_id(id)


class UpdateAddressUseCase:
    """Use case para atualizar Address."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> Address | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteAddressUseCase:
    """Use case para deletar Address."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
