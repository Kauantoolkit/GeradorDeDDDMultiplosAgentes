from fastapi import APIRouter, Depends, HTTPException
from ..application import CreateOrderUseCase, GetOrderUseCase
from ..domain.value_objects import OrderId
from ..domain.events import OrderCreatedEvent
from ..infrastructure import OrderRepository
from ..application.dtos import OrderDTO

router = APIRouter()

order_repository = OrderRepository()
create_order_use_case = CreateOrderUseCase(order_repository)
get_order_use_case = GetOrderUseCase(order_repository)

@router.post('/api/orders', response_model=OrderDTO)
async def create_order(order_dto: OrderDTO):
    create_order_use_case.execute(order_dto)
    return order_dto

@router.get('/api/orders/{order_id}', response_model=OrderDTO)
async def get_order(order_id: OrderId):
    order = get_order_use_case.execute(order_id)
    if order:
        return order
    raise HTTPException(status_code=404, detail='Order not found')