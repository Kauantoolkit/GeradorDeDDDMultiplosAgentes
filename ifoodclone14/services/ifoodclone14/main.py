from fastapi import FastAPI
from services.ifoodclone14.application import CreateOrder
app = FastAPI()
@app.post('/api/orders')
def create_order(request: Request):
    return CreateOrder().execute()
@app.get('/api/products')
def get_products(request: Request):
    return UpdateProduct().execute()
@app.get('/api/products')
def get_product(request: Request, product_id: int):
    return Product().execute(product_id)