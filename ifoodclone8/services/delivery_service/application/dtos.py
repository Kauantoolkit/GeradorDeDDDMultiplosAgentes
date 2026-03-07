"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class DeliveryDTO:
    """DTO para Delivery."""
    id: UUID | None = None
    nome: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateDeliveryDTO:
    """DTO para criação de Delivery."""
    nome: str


@dataclass
class UpdateDeliveryDTO:
    """DTO para atualização de Delivery."""
    nome: str | None = None
