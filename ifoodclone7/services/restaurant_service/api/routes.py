"""
Routes - API Layer
==================
Definição de rotas para restaurant_service.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import RestaurantDTO, CreateRestaurantDTO, UpdateRestaurantDTO
from application.use_cases import (
    CreateRestaurantUseCase,
    GetRestaurantByIdUseCase,
    UpdateRestaurantUseCase,
    DeleteRestaurantUseCase,
)
from infrastructure.repositories import RestaurantRepositoryImpl
from api.schemas import RestaurantSchema, CreateRestaurantSchema
from api.controllers import get_restaurant_repository


router = APIRouter(prefix="/api/restaurant_service", tags=["restaurant_service"])


@router.post("/restaurants", response_model=RestaurantSchema, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    data: CreateRestaurantSchema,
    repository: RestaurantRepositoryImpl = Depends(get_restaurant_repository)
):
    """Cria um novo Restaurant."""
    use_case = CreateRestaurantUseCase(repository)
    entity = await use_case.execute(data.dict())
    return RestaurantSchema.from_orm(entity)


@router.get("/restaurants", response_model=List[RestaurantSchema])
async def list_restaurants(
    repository: RestaurantRepositoryImpl = Depends(get_restaurant_repository)
):
    """Lista todos os Restaurants."""
    entities = await repository.get_all()
    return [RestaurantSchema.from_orm(e) for e in entities]


@router.get("/restaurants/{id}", response_model=RestaurantSchema)
async def get_restaurant(
    id: UUID,
    repository: RestaurantRepositoryImpl = Depends(get_restaurant_repository)
):
    """Busca Restaurant por ID."""
    use_case = GetRestaurantByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"{Restaurant} não encontrado")
    return RestaurantSchema.from_orm(entity)


@router.put("/restaurants/{id}", response_model=RestaurantSchema)
async def update_restaurant(
    id: UUID,
    data: UpdateRestaurantDTO,
    repository: RestaurantRepositoryImpl = Depends(get_restaurant_repository)
):
    """Atualiza Restaurant."""
    use_case = UpdateRestaurantUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail=f"{Restaurant} não encontrado")
    return RestaurantSchema.from_orm(entity)


@router.delete("/restaurants/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(
    id: UUID,
    repository: RestaurantRepositoryImpl = Depends(get_restaurant_repository)
):
    """Deleta Restaurant."""
    use_case = DeleteRestaurantUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail=f"{Restaurant} não encontrado")
