from pydantic import BaseModel
class Payment(BaseModel):
    id: int
    amount: float
    payment_date: str
