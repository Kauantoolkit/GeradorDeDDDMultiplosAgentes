"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class CustomerDTO:
    """DTO para Customer."""
    id: UUID | None = None
    nome: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateCustomerDTO:
    """DTO para criação de Customer."""
    nome: str


@dataclass
class UpdateCustomerDTO:
    """DTO para atualização de Customer."""
    nome: str | None = None
