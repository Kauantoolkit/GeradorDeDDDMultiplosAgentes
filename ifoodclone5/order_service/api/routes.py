from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from order_service.application.use_cases.create_order_use_case import CreateOrderUseCase
from order_service.application.use_cases.get_order_use_case import GetOrderUseCase
from order_service.infrastructure.repositories.order_repository import OrderRepository
from order_service.api.schemas import OrderCreate, Order

router = APIRouter()

@router.post("/orders", response_model=Order)
async def create_order(order: OrderCreate, db: Session = Depends(OrderRepository.get_db)):
    use_case = CreateOrderUseCase(OrderRepository(db))
    new_order = use_case.execute(order.customer_id, order.items)
    return new_order

@router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int, db: Session = Depends(OrderRepository.get_db)):
    use_case = GetOrderUseCase(OrderRepository(db))
    order = use_case.execute(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order