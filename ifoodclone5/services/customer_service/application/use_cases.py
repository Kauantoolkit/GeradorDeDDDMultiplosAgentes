"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio customer.
"""

from uuid import UUID
from domain.customer_entities import Customer


class CreateCustomerUseCase:
    """Use case para criar Customer."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Customer:
        entity = Customer.create(**data)
        return await self.repository.save(entity)


class GetCustomerByIdUseCase:
    """Use case para buscar Customer por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Customer | None:
        return await self.repository.get_by_id(id)


class UpdateCustomerUseCase:
    """Use case para atualizar Customer."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> Customer | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteCustomerUseCase:
    """Use case para deletar Customer."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
