"""DTOs for Invoice."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class InvoiceDTO:
    id: UUID | None = None

@dataclass
class CreateInvoiceDTO:
    pass
