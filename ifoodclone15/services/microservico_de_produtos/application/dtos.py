"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class ProdutosEntityDTO:
    """DTO para ProdutosEntity."""
    id: UUID | None = None
    nome: str | None = None
    preco: float | None = None
    descricao: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateProdutosEntityDTO:
    """DTO para criação de ProdutosEntity."""
    nome: str
    preco: float
    descricao: str | None = None


@dataclass
class UpdateProdutosEntityDTO:
    """DTO para atualização de ProdutosEntity."""
    nome: str | None = None
    preco: float | None = None
    descricao: str | None = None
