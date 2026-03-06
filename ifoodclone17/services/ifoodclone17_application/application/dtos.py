"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class OrderserviceDTO:
    """DTO para Orderservice."""
    id: UUID | None = None
    usuario_id: UUID | None = None
    total: float | None = None
    status: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateOrderserviceDTO:
    """DTO para criação de Orderservice."""
    usuario_id: UUID
    itens: list


@dataclass
class UpdateOrderserviceDTO:
    """DTO para atualização de Orderservice."""
    status: str | None = None
