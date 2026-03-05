"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class OrderSchema(BaseModel):
    """Schema para Order."""
    id: UUID
    usuario_id: UUID
    total: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateOrderSchema(BaseModel):
    """Schema para criação de Order."""
    usuario_id: UUID
    itens: list


class UpdateOrderSchema(BaseModel):
    """Schema para atualização de Order."""
    status: str | None = None
