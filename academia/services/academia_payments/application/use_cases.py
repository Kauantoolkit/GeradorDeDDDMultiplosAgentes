"""Use cases for payments."""
from uuid import UUID
from domain.payments_entities import Payment

class CreatePaymentUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Payment:
        entity = Payment.create(**data)
        return await self.repository.save(entity)

class GetPaymentByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Payment | None:
        return await self.repository.get_by_id(id)
