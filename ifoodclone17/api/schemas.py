from pydantic import BaseModel
class Order(BaseModel):
    id: int
    user_id: int
    product_id: int
class Product(BaseModel):
    id: int
    name: str
    price: float
class User(BaseModel):
    id: int
    username: str
    password: str