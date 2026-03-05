from pydantic import BaseModel
class OrderSchema(BaseModel):
    id: int
    product_id: int
    quantity: int
