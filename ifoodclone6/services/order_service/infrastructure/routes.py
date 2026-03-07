from fastapi import FastAPI
from ..infrastructure.adapters import order_service_adapter

app = FastAPI()

@app.post('/orders/')
def create_order(order_dto):
    return order_service_adapter.create_order(order_dto)

@app.get('/orders/{order_id}')
def get_order(order_id):
    return order_service_adapter.get_order(order_id)