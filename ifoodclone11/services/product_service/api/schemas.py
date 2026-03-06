"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class ProductSchema(BaseModel):
    """Schema para Product."""
    id: UUID
    nome: str
    preco: float
    descricao: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateProductSchema(BaseModel):
    """Schema para criação de Product."""
    nome: str = Field(..., min_length=2, max_length=100)
    preco: float = Field(..., gt=0)
    descricao: str | None = None


class UpdateProductSchema(BaseModel):
    """Schema para atualização de Product."""
    nome: str | None = Field(None, min_length=2, max_length=100)
    preco: float | None = Field(None, gt=0)
    descricao: str | None = None
