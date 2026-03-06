"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class OrdercontrollerDTO:
    """DTO para Ordercontroller."""
    id: UUID | None = None
    usuario_id: UUID | None = None
    total: float | None = None
    status: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateOrdercontrollerDTO:
    """DTO para criação de Ordercontroller."""
    usuario_id: UUID
    itens: list


@dataclass
class UpdateOrdercontrollerDTO:
    """DTO para atualização de Ordercontroller."""
    status: str | None = None
