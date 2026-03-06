"""
Routes - API Layer
==================
Definição de rotas para ifoodclone17_api.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import OrdercontrollerDTO, CreateOrdercontrollerDTO, UpdateOrdercontrollerDTO
from application.use_cases import (
    CreateOrdercontrollerUseCase,
    GetOrdercontrollerByIdUseCase,
    UpdateOrdercontrollerUseCase,
    DeleteOrdercontrollerUseCase,
)
from infrastructure.repositories import OrdercontrollerRepositoryImpl
from api.schemas import OrdercontrollerSchema, CreateOrdercontrollerSchema
from api.controllers import get_ordercontroller_repository


router = APIRouter(prefix="/api/ifoodclone17_api", tags=["ifoodclone17_api"])


@router.post("/ordercontrollers", response_model=OrdercontrollerSchema, status_code=status.HTTP_201_CREATED)
async def create_ordercontroller(
    data: CreateOrdercontrollerSchema,
    repository: OrdercontrollerRepositoryImpl = Depends(get_ordercontroller_repository)
):
    """Cria um novo Ordercontroller."""
    use_case = CreateOrdercontrollerUseCase(repository)
    entity = await use_case.execute(data.dict())
    return OrdercontrollerSchema.from_orm(entity)


@router.get("/ordercontrollers", response_model=List[OrdercontrollerSchema])
async def list_ordercontrollers(
    repository: OrdercontrollerRepositoryImpl = Depends(get_ordercontroller_repository)
):
    """Lista todos os Ordercontrollers."""
    entities = await repository.get_all()
    return [OrdercontrollerSchema.from_orm(e) for e in entities]


@router.get("/ordercontrollers/{id}", response_model=OrdercontrollerSchema)
async def get_ordercontroller(
    id: UUID,
    repository: OrdercontrollerRepositoryImpl = Depends(get_ordercontroller_repository)
):
    """Busca Ordercontroller por ID."""
    use_case = GetOrdercontrollerByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="Ordercontroller não encontrado")
    return OrdercontrollerSchema.from_orm(entity)


@router.put("/ordercontrollers/{id}", response_model=OrdercontrollerSchema)
async def update_ordercontroller(
    id: UUID,
    data: UpdateOrdercontrollerDTO,
    repository: OrdercontrollerRepositoryImpl = Depends(get_ordercontroller_repository)
):
    """Atualiza Ordercontroller."""
    use_case = UpdateOrdercontrollerUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="Ordercontroller não encontrado")
    return OrdercontrollerSchema.from_orm(entity)


@router.delete("/ordercontrollers/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ordercontroller(
    id: UUID,
    repository: OrdercontrollerRepositoryImpl = Depends(get_ordercontroller_repository)
):
    """Deleta Ordercontroller."""
    use_case = DeleteOrdercontrollerUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="Ordercontroller não encontrado")
