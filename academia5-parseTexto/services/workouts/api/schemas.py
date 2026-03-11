"""Schemas for Entity."""
from pydantic import BaseModel

class EntitySchema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
