"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class PaymentDTO:
    """DTO para Payment."""
    id: UUID | None = None
    nome: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreatePaymentDTO:
    """DTO para criação de Payment."""
    nome: str


@dataclass
class UpdatePaymentDTO:
    """DTO para atualização de Payment."""
    nome: str | None = None
