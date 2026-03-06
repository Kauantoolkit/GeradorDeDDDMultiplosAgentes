from pydantic import BaseModel
class OrderRequest(BaseModel):
    data = dict()

class ProductRequest(BaseModel):
    data = dict()