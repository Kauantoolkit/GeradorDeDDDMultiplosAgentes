"""Schemas for Class."""
from pydantic import BaseModel

class ClassSchema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
