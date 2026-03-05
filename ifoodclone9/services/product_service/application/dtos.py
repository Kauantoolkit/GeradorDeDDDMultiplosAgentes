from pydantic import BaseModel
class ProductDto(BaseModel):
    id: int
    name: str
    price: float
    class Config:
        orm_mode = True
