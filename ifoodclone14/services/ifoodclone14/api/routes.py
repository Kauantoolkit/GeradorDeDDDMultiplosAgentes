from fastapi import FastAPI, Request
from services.ifoodclone14.domain import User, Order, Product
from services.ifoodclone14.application import CreateOrder, UpdateProduct
app = FastAPI()
@app.post('/api/orders')
def create_order(request: Request):
    return CreateOrder().execute()
@app.get('/api/products')
def get_products(request: Request):
    return UpdateProduct().execute()
@app.post('/api/products')
def create_product(request: Request):
    return Product().execute()
@app.get('/api/products')
def get_product(request: Request, product_id: int):
    return Product().execute(product_id)