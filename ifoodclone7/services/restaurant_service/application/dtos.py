"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class RestaurantDTO:
    """DTO para Restaurant."""
    id: UUID | None = None
    nome: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateRestaurantDTO:
    """DTO para criação de Restaurant."""
    nome: str


@dataclass
class UpdateRestaurantDTO:
    """DTO para atualização de Restaurant."""
    nome: str | None = None
