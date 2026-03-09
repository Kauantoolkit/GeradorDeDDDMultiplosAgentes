"""Repositories for payment."""
from uuid import UUID
from typing import Optional
from domain.payment_entities import Invoice, InvoiceRepository

class InvoiceRepositoryImpl(InvoiceRepository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[Invoice]:
        pass
    
    async def get_all(self) -> list[Invoice]:
        pass
    
    async def save(self, entity: Invoice) -> Invoice:
        return entity

_repository_instance = None

def get_invoice_repository() -> InvoiceRepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = InvoiceRepositoryImpl()
    return _repository_instance
