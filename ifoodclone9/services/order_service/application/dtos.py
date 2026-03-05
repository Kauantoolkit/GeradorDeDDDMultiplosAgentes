from pydantic import BaseModel
class OrderDto(BaseModel):
    id: int
    product_id: int
    quantity: int
    class Config:
        orm_mode = True
