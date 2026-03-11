"""Schemas for Lesson."""
from pydantic import BaseModel

class LessonSchema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
