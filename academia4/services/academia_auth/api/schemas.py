"""Schemas for Usuario."""
from pydantic import BaseModel

class UsuarioSchema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
