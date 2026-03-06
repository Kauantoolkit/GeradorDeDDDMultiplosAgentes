from fastapi import FastAPI, Request
from services.ifoodclone14.application import CreateOrder, UpdateProduct
from services.ifoodclone14.infrastructure import OrderRepository
app = FastAPI()
@app.post('/api/orders')
def create_order(request: Request):
    order_repo = OrderRepository()
    return order_repo.create_order(request.json['data'])
@app.get('/api/products')
def get_products(request: Request):
    product_repo = ProductRepository()
    return product_repo.get_products(request.query_params)