"""
Schemas - API Layer
==================
Schemas Pydantic para validação de API.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class ReviewSchema(BaseModel):
    """Schema para Review."""
    id: UUID
    nome: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateReviewSchema(BaseModel):
    """Schema para criação de Review."""
    nome: str = Field(..., min_length=2, max_length=100)


class UpdateReviewSchema(BaseModel):
    """Schema para atualização de Review."""
    nome: str | None = Field(None, min_length=2, max_length=100)
