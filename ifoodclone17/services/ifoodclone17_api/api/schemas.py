"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class OrdercontrollerSchema(BaseModel):
    """Schema para Ordercontroller."""
    id: UUID
    usuario_id: UUID
    total: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateOrdercontrollerSchema(BaseModel):
    """Schema para criação de Ordercontroller."""
    usuario_id: UUID
    itens: list


class UpdateOrdercontrollerSchema(BaseModel):
    """Schema para atualização de Ordercontroller."""
    status: str | None = None
