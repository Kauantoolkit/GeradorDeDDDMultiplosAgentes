"""
Routes - API Layer
==================
Definição de rotas para ifoodclone17_application.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import OrderserviceDTO, CreateOrderserviceDTO, UpdateOrderserviceDTO
from application.use_cases import (
    CreateOrderserviceUseCase,
    GetOrderserviceByIdUseCase,
    UpdateOrderserviceUseCase,
    DeleteOrderserviceUseCase,
)
from infrastructure.repositories import OrderserviceRepositoryImpl
from api.schemas import OrderserviceSchema, CreateOrderserviceSchema
from api.controllers import get_orderservice_repository


router = APIRouter(prefix="/api/ifoodclone17_application", tags=["ifoodclone17_application"])


@router.post("/orderservices", response_model=OrderserviceSchema, status_code=status.HTTP_201_CREATED)
async def create_orderservice(
    data: CreateOrderserviceSchema,
    repository: OrderserviceRepositoryImpl = Depends(get_orderservice_repository)
):
    """Cria um novo Orderservice."""
    use_case = CreateOrderserviceUseCase(repository)
    entity = await use_case.execute(data.dict())
    return OrderserviceSchema.from_orm(entity)


@router.get("/orderservices", response_model=List[OrderserviceSchema])
async def list_orderservices(
    repository: OrderserviceRepositoryImpl = Depends(get_orderservice_repository)
):
    """Lista todos os Orderservices."""
    entities = await repository.get_all()
    return [OrderserviceSchema.from_orm(e) for e in entities]


@router.get("/orderservices/{id}", response_model=OrderserviceSchema)
async def get_orderservice(
    id: UUID,
    repository: OrderserviceRepositoryImpl = Depends(get_orderservice_repository)
):
    """Busca Orderservice por ID."""
    use_case = GetOrderserviceByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="Orderservice não encontrado")
    return OrderserviceSchema.from_orm(entity)


@router.put("/orderservices/{id}", response_model=OrderserviceSchema)
async def update_orderservice(
    id: UUID,
    data: UpdateOrderserviceDTO,
    repository: OrderserviceRepositoryImpl = Depends(get_orderservice_repository)
):
    """Atualiza Orderservice."""
    use_case = UpdateOrderserviceUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="Orderservice não encontrado")
    return OrderserviceSchema.from_orm(entity)


@router.delete("/orderservices/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_orderservice(
    id: UUID,
    repository: OrderserviceRepositoryImpl = Depends(get_orderservice_repository)
):
    """Deleta Orderservice."""
    use_case = DeleteOrderserviceUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="Orderservice não encontrado")
