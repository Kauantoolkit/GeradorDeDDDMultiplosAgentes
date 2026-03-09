"""Mappers for payment."""
from application.dtos import InvoiceDTO
from domain.payment_entities import Invoice

class InvoiceMapper:
    @staticmethod
    def to_dto(entity: Invoice) -> InvoiceDTO:
        return InvoiceDTO(id=entity.id)
