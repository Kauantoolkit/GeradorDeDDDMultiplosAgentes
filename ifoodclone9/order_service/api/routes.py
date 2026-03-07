from fastapi import APIRouter, Depends, HTTPException
from application.use_cases.create_order_use_case import CreateOrderUseCase
from application.use_cases.get_order_use_case import GetOrderUseCase
from domain.entities.order import Order
from domain.entities.order_item import OrderItem
from infrastructure.repositories.order_repository import OrderRepository

router = APIRouter()

order_repository = OrderRepository()

@router.post("/api/orders")
def create_order(order_id: str, customer_id: str, items: list[dict], status: str, use_case: CreateOrderUseCase = Depends()):
    order_items = [OrderItem(item['product_id'], item['quantity']) for item in items]
    order = use_case.execute(order_id, customer_id, order_items, status)
    return order

@router.get("/api/orders/{order_id}")
def get_order(order_id: str, use_case: GetOrderUseCase = Depends()):
    order = use_case.execute(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order