"""Schemas for User."""
from pydantic import BaseModel

class UserSchema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
