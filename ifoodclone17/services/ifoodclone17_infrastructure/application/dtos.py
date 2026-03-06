"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class DatabaseDTO:
    """DTO para Database."""
    id: UUID | None = None
    nome: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateDatabaseDTO:
    """DTO para criação de Database."""
    nome: str


@dataclass
class UpdateDatabaseDTO:
    """DTO para atualização de Database."""
    nome: str | None = None
