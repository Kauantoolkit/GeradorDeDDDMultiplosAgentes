"""Schemas for Invoice."""
from pydantic import BaseModel

class InvoiceSchema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
