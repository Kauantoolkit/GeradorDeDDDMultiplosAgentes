from pydantic import BaseModel

class Restaurant(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    class Config:
        orm_mode = True