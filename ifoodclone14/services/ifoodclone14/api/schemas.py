from pydantic import BaseModel
class OrderRequest(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total: float
class ProductRequest(BaseModel):
    id: int
    name: str
    price: float
class ShippingRequest(BaseModel):
    id: int
    address_id: int
    shipping_method: str
    cost: float