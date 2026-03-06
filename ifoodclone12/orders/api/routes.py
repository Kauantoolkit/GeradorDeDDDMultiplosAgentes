from fastapi import FastAPI
from orders.application.use_cases import CreateOrderUseCase
app = FastAPI()
@app.post('/api/orders', response_model=Order)
def create_order(order: Order):
    use_case = CreateOrderUseCase(order)
    use_case.execute()
    return order