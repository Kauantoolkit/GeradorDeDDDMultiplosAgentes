"""Mappers for payments."""
from application.dtos import PaymentDTO
from domain.payments_entities import Payment

class PaymentMapper:
    @staticmethod
    def to_dto(entity: Payment) -> PaymentDTO:
        return PaymentDTO(id=entity.id)
