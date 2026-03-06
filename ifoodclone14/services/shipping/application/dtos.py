"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class AddressDTO:
    """DTO para Address."""
    id: UUID | None = None
    nome: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateAddressDTO:
    """DTO para criação de Address."""
    nome: str


@dataclass
class UpdateAddressDTO:
    """DTO para atualização de Address."""
    nome: str | None = None
