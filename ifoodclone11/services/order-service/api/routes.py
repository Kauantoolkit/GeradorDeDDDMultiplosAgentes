from fastapi import FastAPI, HTTPException
from application import CreateOrder
app = FastAPI()
@app.post('/api/orders', response_model=Order)
async def create_order(order_data: Order):
    use_case = CreateOrder()
    order = use_case.execute(order_data)
    return order
