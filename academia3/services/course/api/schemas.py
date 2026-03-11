"""Schemas for Course."""
from pydantic import BaseModel

class CourseSchema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
