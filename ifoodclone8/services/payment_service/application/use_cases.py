"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio payment_domain.
"""

from uuid import UUID
from domain.payment_domain_entities import Payment


class CreatePaymentUseCase:
    """Use case para criar Payment."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Payment:
        entity = Payment.create(**data)
        return await self.repository.save(entity)


class GetPaymentByIdUseCase:
    """Use case para buscar Payment por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Payment | None:
        return await self.repository.get_by_id(id)


class UpdatePaymentUseCase:
    """Use case para atualizar Payment."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> Payment | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeletePaymentUseCase:
    """Use case para deletar Payment."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
