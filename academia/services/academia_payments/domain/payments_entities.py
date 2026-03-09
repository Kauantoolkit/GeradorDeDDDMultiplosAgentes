"""Entity: Payment"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Payment:
    """Domain entity for payments."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Payment":
        now = datetime.now()
        return Payment(
            id=uuid4(),
            created_at=now,
            updated_at=now,
            **{k: v for k, v in kwargs.items() if k not in ['id', 'created_at', 'updated_at']}
        )
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class PaymentRepository:
    """Repository interface for Payment."""
    async def get_by_id(self, id: UUID) -> "Payment | None":
        raise NotImplementedError
    async def get_all(self) -> list["Payment"]:
        raise NotImplementedError
    async def save(self, entity: "Payment") -> "Payment":
        raise NotImplementedError


"""Entity: Invoice"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Invoice:
    """Domain entity for payments."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Invoice":
        now = datetime.now()
        return Invoice(
            id=uuid4(),
            created_at=now,
            updated_at=now,
            **{k: v for k, v in kwargs.items() if k not in ['id', 'created_at', 'updated_at']}
        )
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class InvoiceRepository:
    """Repository interface for Invoice."""
    async def get_by_id(self, id: UUID) -> "Invoice | None":
        raise NotImplementedError
    async def get_all(self) -> list["Invoice"]:
        raise NotImplementedError
    async def save(self, entity: "Invoice") -> "Invoice":
        raise NotImplementedError
