"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class PaymentSchema(BaseModel):
    """Schema para Payment."""
    id: UUID
    nome: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreatePaymentSchema(BaseModel):
    """Schema para criação de Payment."""
    nome: str = Field(..., min_length=2, max_length=100)


class UpdatePaymentSchema(BaseModel):
    """Schema para atualização de Payment."""
    nome: str | None = Field(None, min_length=2, max_length=100)
