from pydantic import BaseModel
class PaymentRequest(BaseModel):
    amount: float
    payment_method: str
    payment_status: str