"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class UsuariosEntityDTO:
    """DTO para UsuariosEntity."""
    id: UUID | None = None
    nome: str | None = None
    email: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateUsuariosEntityDTO:
    """DTO para criação de UsuariosEntity."""
    nome: str
    email: str
    senha: str


@dataclass
class UpdateUsuariosEntityDTO:
    """DTO para atualização de UsuariosEntity."""
    nome: str | None = None
    email: str | None = None
