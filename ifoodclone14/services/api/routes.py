from fastapi import FastAPI, Request
from services.ifoodclone14.application import CreateOrder, UpdateProduct
app = FastAPI()
@app.post('/api/orders')
def create_order(request: Request):
    return CreateOrder().execute()
@app.get('/api/products')
def get_products(request: Request):
    return UpdateProduct().execute()