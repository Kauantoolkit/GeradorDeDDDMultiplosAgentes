"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class OrderDTO:
    """DTO para Order."""
    id: UUID | None = None
    usuario_id: UUID | None = None
    total: float | None = None
    status: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateOrderDTO:
    """DTO para criação de Order."""
    usuario_id: UUID
    itens: list


@dataclass
class UpdateOrderDTO:
    """DTO para atualização de Order."""
    status: str | None = None
