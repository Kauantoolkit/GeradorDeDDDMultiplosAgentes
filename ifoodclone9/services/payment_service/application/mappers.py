"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import PaymentDTO, CreatePaymentDTO
from domain.payment_entities import Payment


class PaymentMapper:
    """Mapper para Payment."""
    
    @staticmethod
    def to_dto(entity: Payment) -> PaymentDTO:
        return PaymentDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: PaymentDTO) -> Payment:
        return Payment(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreatePaymentDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
