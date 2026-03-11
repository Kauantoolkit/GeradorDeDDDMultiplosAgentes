"""Schemas for Aluno."""
from pydantic import BaseModel

class AlunoSchema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
