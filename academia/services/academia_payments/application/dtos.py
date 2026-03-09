"""DTOs for Payment."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class PaymentDTO:
    id: UUID | None = None

@dataclass
class CreatePaymentDTO:
    pass
