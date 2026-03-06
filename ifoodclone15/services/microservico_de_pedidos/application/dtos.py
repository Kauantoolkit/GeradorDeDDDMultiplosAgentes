"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class PedidosEntityDTO:
    """DTO para PedidosEntity."""
    id: UUID | None = None
    usuario_id: UUID | None = None
    total: float | None = None
    status: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreatePedidosEntityDTO:
    """DTO para criação de PedidosEntity."""
    usuario_id: UUID
    itens: list


@dataclass
class UpdatePedidosEntityDTO:
    """DTO para atualização de PedidosEntity."""
    status: str | None = None
