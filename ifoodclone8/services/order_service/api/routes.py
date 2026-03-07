"""
API Routes
=========
Rotas da API para o serviço de pedidos.
"""

import sys
from pathlib import Path

# Adiciona o diretório do serviço ao path
service_path = Path(__file__).parent.parent
if str(service_path) not in sys.path:
    sys.path.insert(0, str(service_path))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from infrastructure.database import SessionLocal
from infrastructure.repositories import OrderRepository, ProductRepository
from application.use_cases.create_order_use_case import (
    CreateOrderUseCase,
    GetOrderUseCase,
    ListOrdersUseCase,
    UpdateOrderStatusUseCase,
    CancelOrderUseCase
)
from application.dtos import CreateOrderDTO, UpdateOrderDTO, OrderDTO

router = APIRouter(prefix="/api/order_service")


def get_db():
    """Dependência para obter a sessão do banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/orders", response_model=dict)
async def create_order(dto: CreateOrderDTO, db: Session = Depends(get_db)):
    """
    Cria um novo pedido.
    """
    repository = OrderRepository(db)
    use_case = CreateOrderUseCase(repository)
    result = use_case.execute(dto)
    return result


@router.get("/orders/{order_id}", response_model=dict)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Busca um pedido pelo ID.
    """
    repository = OrderRepository(db)
    use_case = GetOrderUseCase(repository)
    order = use_case.execute(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return order


@router.get("/orders", response_model=List[dict])
async def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista pedidos com paginação.
    """
    repository = OrderRepository(db)
    use_case = ListOrdersUseCase(repository)
    return use_case.execute(skip=skip, limit=limit)


@router.patch("/orders/{order_id}/status", response_model=dict)
async def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    """
    Atualiza o status de um pedido.
    """
    repository = OrderRepository(db)
    use_case = UpdateOrderStatusUseCase(repository)
    result = use_case.execute(order_id, status)
    if not result:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return result


@router.post("/orders/{order_id}/cancel", response_model=dict)
async def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """
    Cancela um pedido.
    """
    repository = OrderRepository(db)
    use_case = CancelOrderUseCase(repository)
    success = use_case.execute(order_id)
    if not success:
        raise HTTPException(status_code=400, detail="Não foi possível cancelar o pedido")
    return {"message": "Pedido cancelado com sucesso", "order_id": order_id}


@router.get("/api/health")
async def health_check():
    """
    Verifica a saúde do serviço.
    """
    return {"status": "healthy", "service": "order_service"}

