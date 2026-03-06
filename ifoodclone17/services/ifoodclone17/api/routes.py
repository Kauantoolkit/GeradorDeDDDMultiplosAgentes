"""
Routes - API Layer
==================
Definição de rotas para ifoodclone17.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import OrderDTO, CreateOrderDTO, UpdateOrderDTO
from application.use_cases import (
    CreateOrderUseCase,
    GetOrderByIdUseCase,
    UpdateOrderUseCase,
    DeleteOrderUseCase,
)
from infrastructure.repositories import OrderRepositoryImpl
from api.schemas import OrderSchema, CreateOrderSchema
from api.controllers import get_order_repository


router = APIRouter(prefix="/api/ifoodclone17", tags=["ifoodclone17"])


@router.post("/orders", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def create_order(
    data: CreateOrderSchema,
    repository: OrderRepositoryImpl = Depends(get_order_repository)
):
    """Cria um novo Order."""
    use_case = CreateOrderUseCase(repository)
    entity = await use_case.execute(data.dict())
    return OrderSchema.from_orm(entity)


@router.get("/orders", response_model=List[OrderSchema])
async def list_orders(
    repository: OrderRepositoryImpl = Depends(get_order_repository)
):
    """Lista todos os Orders."""
    entities = await repository.get_all()
    return [OrderSchema.from_orm(e) for e in entities]


@router.get("/orders/{id}", response_model=OrderSchema)
async def get_order(
    id: UUID,
    repository: OrderRepositoryImpl = Depends(get_order_repository)
):
    """Busca Order por ID."""
    use_case = GetOrderByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="Order não encontrado")
    return OrderSchema.from_orm(entity)


@router.put("/orders/{id}", response_model=OrderSchema)
async def update_order(
    id: UUID,
    data: UpdateOrderDTO,
    repository: OrderRepositoryImpl = Depends(get_order_repository)
):
    """Atualiza Order."""
    use_case = UpdateOrderUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="Order não encontrado")
    return OrderSchema.from_orm(entity)


@router.delete("/orders/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    id: UUID,
    repository: OrderRepositoryImpl = Depends(get_order_repository)
):
    """Deleta Order."""
    use_case = DeleteOrderUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="Order não encontrado")
