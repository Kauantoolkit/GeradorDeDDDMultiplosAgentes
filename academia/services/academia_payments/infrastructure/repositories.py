"""Repositories for payments."""
from uuid import UUID
from typing import Optional
from domain.payments_entities import Payment, PaymentRepository

class PaymentRepositoryImpl(PaymentRepository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[Payment]:
        pass
    
    async def get_all(self) -> list[Payment]:
        pass
    
    async def save(self, entity: Payment) -> Payment:
        return entity

_repository_instance = None

def get_payment_repository() -> PaymentRepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = PaymentRepositoryImpl()
    return _repository_instance
