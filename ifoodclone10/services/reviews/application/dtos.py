"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class ReviewDTO:
    """DTO para Review."""
    id: UUID | None = None
    nome: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateReviewDTO:
    """DTO para criação de Review."""
    nome: str


@dataclass
class UpdateReviewDTO:
    """DTO para atualização de Review."""
    nome: str | None = None
