"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class UsuariosEntitySchema(BaseModel):
    """Schema para UsuariosEntity."""
    id: UUID
    nome: str
    email: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateUsuariosEntitySchema(BaseModel):
    """Schema para criação de UsuariosEntity."""
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    senha: str = Field(..., min_length=6)


class UpdateUsuariosEntitySchema(BaseModel):
    """Schema para atualização de UsuariosEntity."""
    nome: str | None = Field(None, min_length=2, max_length=100)
    email: EmailStr | None = None
