"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class PedidosEntitySchema(BaseModel):
    """Schema para PedidosEntity."""
    id: UUID
    usuario_id: UUID
    total: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreatePedidosEntitySchema(BaseModel):
    """Schema para criação de PedidosEntity."""
    usuario_id: UUID
    itens: list


class UpdatePedidosEntitySchema(BaseModel):
    """Schema para atualização de PedidosEntity."""
    status: str | None = None
