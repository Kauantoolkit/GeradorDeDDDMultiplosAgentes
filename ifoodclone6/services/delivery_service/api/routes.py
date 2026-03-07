"""
Routes - API Layer
==================
Definição de rotas para delivery_service.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import DeliveryDTO, CreateDeliveryDTO, UpdateDeliveryDTO
from application.use_cases import (
    CreateDeliveryUseCase,
    GetDeliveryByIdUseCase,
    UpdateDeliveryUseCase,
    DeleteDeliveryUseCase,
)
from infrastructure.repositories import DeliveryRepositoryImpl
from api.schemas import DeliverySchema, CreateDeliverySchema
from api.controllers import get_delivery_repository


router = APIRouter(prefix="/api/delivery_service", tags=["delivery_service"])


@router.post("/deliverys", response_model=DeliverySchema, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    data: CreateDeliverySchema,
    repository: DeliveryRepositoryImpl = Depends(get_delivery_repository)
):
    """Cria um novo Delivery."""
    use_case = CreateDeliveryUseCase(repository)
    entity = await use_case.execute(data.dict())
    return DeliverySchema.from_orm(entity)


@router.get("/deliverys", response_model=List[DeliverySchema])
async def list_deliverys(
    repository: DeliveryRepositoryImpl = Depends(get_delivery_repository)
):
    """Lista todos os Deliverys."""
    entities = await repository.get_all()
    return [DeliverySchema.from_orm(e) for e in entities]


@router.get("/deliverys/{id}", response_model=DeliverySchema)
async def get_delivery(
    id: UUID,
    repository: DeliveryRepositoryImpl = Depends(get_delivery_repository)
):
    """Busca Delivery por ID."""
    use_case = GetDeliveryByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"{Delivery} não encontrado")
    return DeliverySchema.from_orm(entity)


@router.put("/deliverys/{id}", response_model=DeliverySchema)
async def update_delivery(
    id: UUID,
    data: UpdateDeliveryDTO,
    repository: DeliveryRepositoryImpl = Depends(get_delivery_repository)
):
    """Atualiza Delivery."""
    use_case = UpdateDeliveryUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail=f"{Delivery} não encontrado")
    return DeliverySchema.from_orm(entity)


@router.delete("/deliverys/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_delivery(
    id: UUID,
    repository: DeliveryRepositoryImpl = Depends(get_delivery_repository)
):
    """Deleta Delivery."""
    use_case = DeleteDeliveryUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail=f"{Delivery} não encontrado")
