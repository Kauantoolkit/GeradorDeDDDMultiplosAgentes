"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class UserDTO:
    """DTO para User."""
    id: UUID | None = None
    nome: str | None = None
    email: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateUserDTO:
    """DTO para criação de User."""
    nome: str
    email: str
    senha: str


@dataclass
class UpdateUserDTO:
    """DTO para atualização de User."""
    nome: str | None = None
    email: str | None = None
