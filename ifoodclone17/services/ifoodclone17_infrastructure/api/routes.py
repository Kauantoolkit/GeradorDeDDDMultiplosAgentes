"""
Routes - API Layer
==================
Definição de rotas para ifoodclone17_infrastructure.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import DatabaseDTO, CreateDatabaseDTO, UpdateDatabaseDTO
from application.use_cases import (
    CreateDatabaseUseCase,
    GetDatabaseByIdUseCase,
    UpdateDatabaseUseCase,
    DeleteDatabaseUseCase,
)
from infrastructure.repositories import DatabaseRepositoryImpl
from api.schemas import DatabaseSchema, CreateDatabaseSchema
from api.controllers import get_database_repository


router = APIRouter(prefix="/api/ifoodclone17_infrastructure", tags=["ifoodclone17_infrastructure"])


@router.post("/databases", response_model=DatabaseSchema, status_code=status.HTTP_201_CREATED)
async def create_database(
    data: CreateDatabaseSchema,
    repository: DatabaseRepositoryImpl = Depends(get_database_repository)
):
    """Cria um novo Database."""
    use_case = CreateDatabaseUseCase(repository)
    entity = await use_case.execute(data.dict())
    return DatabaseSchema.from_orm(entity)


@router.get("/databases", response_model=List[DatabaseSchema])
async def list_databases(
    repository: DatabaseRepositoryImpl = Depends(get_database_repository)
):
    """Lista todos os Databases."""
    entities = await repository.get_all()
    return [DatabaseSchema.from_orm(e) for e in entities]


@router.get("/databases/{id}", response_model=DatabaseSchema)
async def get_database(
    id: UUID,
    repository: DatabaseRepositoryImpl = Depends(get_database_repository)
):
    """Busca Database por ID."""
    use_case = GetDatabaseByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="Database não encontrado")
    return DatabaseSchema.from_orm(entity)


@router.put("/databases/{id}", response_model=DatabaseSchema)
async def update_database(
    id: UUID,
    data: UpdateDatabaseDTO,
    repository: DatabaseRepositoryImpl = Depends(get_database_repository)
):
    """Atualiza Database."""
    use_case = UpdateDatabaseUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="Database não encontrado")
    return DatabaseSchema.from_orm(entity)


@router.delete("/databases/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_database(
    id: UUID,
    repository: DatabaseRepositoryImpl = Depends(get_database_repository)
):
    """Deleta Database."""
    use_case = DeleteDatabaseUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="Database não encontrado")
