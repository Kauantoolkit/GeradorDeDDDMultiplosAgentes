from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..domain.value_objects import OrderId
from ..infrastructure.database import SessionLocal
from ..application.use_cases import CreateOrderUseCase
from ..application.dtos import CreateOrderDTO

router = APIRouter()

@router.post('/api/orders', response_model=CreateOrderDTO)
async def create_order(dto: CreateOrderDTO, db: Session = Depends(SessionLocal)):
    use_case = CreateOrderUseCase(order_repository=order_repository)
    use_case.execute(dto)
    return dto

@router.get('/api/orders/{order_id}', response_model=CreateOrderDTO)
async def get_order(order_id: str, db: Session = Depends(SessionLocal)):
    order_id = OrderId(order_id)
    order = order_repository.get_by_id(order_id)
    if order:
        return order
    raise HTTPException(status_code=404, detail='Order not found')