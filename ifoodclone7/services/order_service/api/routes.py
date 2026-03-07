from fastapi import APIRouter, Depends
from application.use_cases import CreateOrderUseCase, GetOrderUseCase
from domain.value_objects import OrderId, CustomerId, RestaurantId, OrderItem

router = APIRouter()

@router.post("/orders")
def create_order(order: Order, create_order_use_case: CreateOrderUseCase = Depends()):
    create_order_use_case.execute(order)
    return {"message": "Order created"}

@router.get("/orders/{order_id}")
def get_order(order_id: OrderId, get_order_use_case: GetOrderUseCase = Depends()):
    order = get_order_use_case.execute(order_id)
    return order
