"""Schemas for Payment."""
from pydantic import BaseModel

class PaymentSchema(BaseModel):
    id: str
    
    class Config:
        from_attributes = True
