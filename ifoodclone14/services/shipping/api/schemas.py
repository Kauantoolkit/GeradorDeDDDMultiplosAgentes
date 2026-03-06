from pydantic import BaseModel
class ShippingRequest(BaseModel):
    address_id: int
    shipping_method: str
    cost: float