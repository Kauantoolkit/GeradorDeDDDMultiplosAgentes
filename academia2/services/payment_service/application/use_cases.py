"""Use cases for payment."""
from uuid import UUID
from domain.payment_entities import Invoice

class CreateInvoiceUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Invoice:
        entity = Invoice.create(**data)
        return await self.repository.save(entity)

class GetInvoiceByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Invoice | None:
        return await self.repository.get_by_id(id)
