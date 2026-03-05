from fastapi import FastAPI
from services.order_service.application.use_cases import CreateOrderUseCase
from services.order_service.application.dtos import OrderDto
app = FastAPI()
@app.post('/api/orders', response_model=OrderDto)
def create_order(order: OrderDto):
    use_case = CreateOrderUseCase(order)
    return use_case.execute()
