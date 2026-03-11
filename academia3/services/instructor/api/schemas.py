"""Schemas for Instructor."""
from pydantic import BaseModel

class InstructorSchema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
