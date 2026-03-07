from fastapi import APIRouter, Depends, HTTPException
from application.use_cases import CreateOrderUseCase, GetOrderUseCase
from infrastructure.repositories import OrderRepository
from domain.entities import Order

router = APIRouter()

order_repository = OrderRepository()
create_order_use_case = CreateOrderUseCase(order_repository)
get_order_use_case = GetOrderUseCase(order_repository)

@router.post('/api/orders', response_model=Order)
async def create_order(order_id: str, customer_id: str, items: list):
    order = create_order_use_case.execute(order_id, customer_id, items)
    return order

@router.get('/api/orders/{order_id}', response_model=Order)
async def get_order(order_id: str):
    order = get_order_use_case.execute(order_id)
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')
    return order