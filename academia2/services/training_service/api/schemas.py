"""Schemas for Session."""
from pydantic import BaseModel

class SessionSchema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
