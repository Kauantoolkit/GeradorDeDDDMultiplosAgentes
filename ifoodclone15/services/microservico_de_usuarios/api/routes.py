"""
Routes - API Layer
==================
Definição de rotas para microservico_de_usuarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import UsuariosEntityDTO, CreateUsuariosEntityDTO, UpdateUsuariosEntityDTO
from application.use_cases import (
    CreateUsuariosEntityUseCase,
    GetUsuariosEntityByIdUseCase,
    UpdateUsuariosEntityUseCase,
    DeleteUsuariosEntityUseCase,
)
from infrastructure.repositories import UsuariosEntityRepositoryImpl
from api.schemas import UsuariosEntitySchema, CreateUsuariosEntitySchema
from api.controllers import get_usuariosentity_repository


router = APIRouter(prefix="/api/microservico_de_usuarios", tags=["microservico_de_usuarios"])


@router.post("/usuariosentitys", response_model=UsuariosEntitySchema, status_code=status.HTTP_201_CREATED)
async def create_usuariosentity(
    data: CreateUsuariosEntitySchema,
    repository: UsuariosEntityRepositoryImpl = Depends(get_usuariosentity_repository)
):
    """Cria um novo UsuariosEntity."""
    use_case = CreateUsuariosEntityUseCase(repository)
    entity = await use_case.execute(data.dict())
    return UsuariosEntitySchema.from_orm(entity)


@router.get("/usuariosentitys", response_model=List[UsuariosEntitySchema])
async def list_usuariosentitys(
    repository: UsuariosEntityRepositoryImpl = Depends(get_usuariosentity_repository)
):
    """Lista todos os UsuariosEntitys."""
    entities = await repository.get_all()
    return [UsuariosEntitySchema.from_orm(e) for e in entities]


@router.get("/usuariosentitys/{id}", response_model=UsuariosEntitySchema)
async def get_usuariosentity(
    id: UUID,
    repository: UsuariosEntityRepositoryImpl = Depends(get_usuariosentity_repository)
):
    """Busca UsuariosEntity por ID."""
    use_case = GetUsuariosEntityByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="UsuariosEntity não encontrado")
    return UsuariosEntitySchema.from_orm(entity)


@router.put("/usuariosentitys/{id}", response_model=UsuariosEntitySchema)
async def update_usuariosentity(
    id: UUID,
    data: UpdateUsuariosEntityDTO,
    repository: UsuariosEntityRepositoryImpl = Depends(get_usuariosentity_repository)
):
    """Atualiza UsuariosEntity."""
    use_case = UpdateUsuariosEntityUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="UsuariosEntity não encontrado")
    return UsuariosEntitySchema.from_orm(entity)


@router.delete("/usuariosentitys/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuariosentity(
    id: UUID,
    repository: UsuariosEntityRepositoryImpl = Depends(get_usuariosentity_repository)
):
    """Deleta UsuariosEntity."""
    use_case = DeleteUsuariosEntityUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="UsuariosEntity não encontrado")
