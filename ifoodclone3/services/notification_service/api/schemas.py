"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class NotificationSchema(BaseModel):
    """Schema para Notification."""
    id: UUID
    nome: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateNotificationSchema(BaseModel):
    """Schema para criação de Notification."""
    nome: str = Field(..., min_length=2, max_length=100)


class UpdateNotificationSchema(BaseModel):
    """Schema para atualização de Notification."""
    nome: str | None = Field(None, min_length=2, max_length=100)
