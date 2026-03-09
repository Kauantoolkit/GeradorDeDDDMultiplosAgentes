"""Schemas for Member."""
from pydantic import BaseModel

class MemberSchema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
