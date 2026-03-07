"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class CustomerSchema(BaseModel):
    """Schema para Customer."""
    id: UUID
    nome: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateCustomerSchema(BaseModel):
    """Schema para criação de Customer."""
    nome: str = Field(..., min_length=2, max_length=100)


class UpdateCustomerSchema(BaseModel):
    """Schema para atualização de Customer."""
    nome: str | None = Field(None, min_length=2, max_length=100)
