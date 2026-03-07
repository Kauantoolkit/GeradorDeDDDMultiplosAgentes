"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class RestaurantSchema(BaseModel):
    """Schema para Restaurant."""
    id: UUID
    nome: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateRestaurantSchema(BaseModel):
    """Schema para criação de Restaurant."""
    nome: str = Field(..., min_length=2, max_length=100)


class UpdateRestaurantSchema(BaseModel):
    """Schema para atualização de Restaurant."""
    nome: str | None = Field(None, min_length=2, max_length=100)
