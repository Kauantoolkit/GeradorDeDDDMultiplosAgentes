"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class DeliverySchema(BaseModel):
    """Schema para Delivery."""
    id: UUID
    nome: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateDeliverySchema(BaseModel):
    """Schema para criação de Delivery."""
    nome: str = Field(..., min_length=2, max_length=100)


class UpdateDeliverySchema(BaseModel):
    """Schema para atualização de Delivery."""
    nome: str | None = Field(None, min_length=2, max_length=100)
