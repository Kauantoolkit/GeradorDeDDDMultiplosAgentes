"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class DatabaseSchema(BaseModel):
    """Schema para Database."""
    id: UUID
    nome: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateDatabaseSchema(BaseModel):
    """Schema para criação de Database."""
    nome: str = Field(..., min_length=2, max_length=100)


class UpdateDatabaseSchema(BaseModel):
    """Schema para atualização de Database."""
    nome: str | None = Field(None, min_length=2, max_length=100)
