"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class OrdensEntitySchema(BaseModel):
    """Schema para OrdensEntity."""
    id: UUID
    nome: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateOrdensEntitySchema(BaseModel):
    """Schema para criação de OrdensEntity."""
    nome: str = Field(..., min_length=2, max_length=100)


class UpdateOrdensEntitySchema(BaseModel):
    """Schema para atualização de OrdensEntity."""
    nome: str | None = Field(None, min_length=2, max_length=100)
