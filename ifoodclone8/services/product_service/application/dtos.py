"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class ProductDTO:
    """DTO para Product."""
    id: UUID | None = None
    nome: str | None = None
    preco: float | None = None
    descricao: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateProductDTO:
    """DTO para criação de Product."""
    nome: str
    preco: float
    descricao: str | None = None


@dataclass
class UpdateProductDTO:
    """DTO para atualização de Product."""
    nome: str | None = None
    preco: float | None = None
    descricao: str | None = None
