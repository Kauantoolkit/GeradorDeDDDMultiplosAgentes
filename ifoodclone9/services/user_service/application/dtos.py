from pydantic import BaseModel
class UserDto(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        orm_mode = True
