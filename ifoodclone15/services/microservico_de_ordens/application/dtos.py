"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class OrdensEntityDTO:
    """DTO para OrdensEntity."""
    id: UUID | None = None
    nome: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateOrdensEntityDTO:
    """DTO para criação de OrdensEntity."""
    nome: str


@dataclass
class UpdateOrdensEntityDTO:
    """DTO para atualização de OrdensEntity."""
    nome: str | None = None
