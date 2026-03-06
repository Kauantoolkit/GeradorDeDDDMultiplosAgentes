"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class OrderserviceSchema(BaseModel):
    """Schema para Orderservice."""
    id: UUID
    usuario_id: UUID
    total: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateOrderserviceSchema(BaseModel):
    """Schema para criação de Orderservice."""
    usuario_id: UUID
    itens: list


class UpdateOrderserviceSchema(BaseModel):
    """Schema para atualização de Orderservice."""
    status: str | None = None
