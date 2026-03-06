"""
Routes - API Layer
==================
Definição de rotas para microservico_de_ordens.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import OrdensEntityDTO, CreateOrdensEntityDTO, UpdateOrdensEntityDTO
from application.use_cases import (
    CreateOrdensEntityUseCase,
    GetOrdensEntityByIdUseCase,
    UpdateOrdensEntityUseCase,
    DeleteOrdensEntityUseCase,
)
from infrastructure.repositories import OrdensEntityRepositoryImpl
from api.schemas import OrdensEntitySchema, CreateOrdensEntitySchema
from api.controllers import get_ordensentity_repository


router = APIRouter(prefix="/api/microservico_de_ordens", tags=["microservico_de_ordens"])


@router.post("/ordensentitys", response_model=OrdensEntitySchema, status_code=status.HTTP_201_CREATED)
async def create_ordensentity(
    data: CreateOrdensEntitySchema,
    repository: OrdensEntityRepositoryImpl = Depends(get_ordensentity_repository)
):
    """Cria um novo OrdensEntity."""
    use_case = CreateOrdensEntityUseCase(repository)
    entity = await use_case.execute(data.dict())
    return OrdensEntitySchema.from_orm(entity)


@router.get("/ordensentitys", response_model=List[OrdensEntitySchema])
async def list_ordensentitys(
    repository: OrdensEntityRepositoryImpl = Depends(get_ordensentity_repository)
):
    """Lista todos os OrdensEntitys."""
    entities = await repository.get_all()
    return [OrdensEntitySchema.from_orm(e) for e in entities]


@router.get("/ordensentitys/{id}", response_model=OrdensEntitySchema)
async def get_ordensentity(
    id: UUID,
    repository: OrdensEntityRepositoryImpl = Depends(get_ordensentity_repository)
):
    """Busca OrdensEntity por ID."""
    use_case = GetOrdensEntityByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="OrdensEntity não encontrado")
    return OrdensEntitySchema.from_orm(entity)


@router.put("/ordensentitys/{id}", response_model=OrdensEntitySchema)
async def update_ordensentity(
    id: UUID,
    data: UpdateOrdensEntityDTO,
    repository: OrdensEntityRepositoryImpl = Depends(get_ordensentity_repository)
):
    """Atualiza OrdensEntity."""
    use_case = UpdateOrdensEntityUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="OrdensEntity não encontrado")
    return OrdensEntitySchema.from_orm(entity)


@router.delete("/ordensentitys/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ordensentity(
    id: UUID,
    repository: OrdensEntityRepositoryImpl = Depends(get_ordensentity_repository)
):
    """Deleta OrdensEntity."""
    use_case = DeleteOrdensEntityUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="OrdensEntity não encontrado")
