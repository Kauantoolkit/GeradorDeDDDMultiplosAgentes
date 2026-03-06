"""
Routes - API Layer
==================
Definição de rotas para microservico_de_pedidos.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import PedidosEntityDTO, CreatePedidosEntityDTO, UpdatePedidosEntityDTO
from application.use_cases import (
    CreatePedidosEntityUseCase,
    GetPedidosEntityByIdUseCase,
    UpdatePedidosEntityUseCase,
    DeletePedidosEntityUseCase,
)
from infrastructure.repositories import PedidosEntityRepositoryImpl
from api.schemas import PedidosEntitySchema, CreatePedidosEntitySchema
from api.controllers import get_pedidosentity_repository


router = APIRouter(prefix="/api/microservico_de_pedidos", tags=["microservico_de_pedidos"])


@router.post("/pedidosentitys", response_model=PedidosEntitySchema, status_code=status.HTTP_201_CREATED)
async def create_pedidosentity(
    data: CreatePedidosEntitySchema,
    repository: PedidosEntityRepositoryImpl = Depends(get_pedidosentity_repository)
):
    """Cria um novo PedidosEntity."""
    use_case = CreatePedidosEntityUseCase(repository)
    entity = await use_case.execute(data.dict())
    return PedidosEntitySchema.from_orm(entity)


@router.get("/pedidosentitys", response_model=List[PedidosEntitySchema])
async def list_pedidosentitys(
    repository: PedidosEntityRepositoryImpl = Depends(get_pedidosentity_repository)
):
    """Lista todos os PedidosEntitys."""
    entities = await repository.get_all()
    return [PedidosEntitySchema.from_orm(e) for e in entities]


@router.get("/pedidosentitys/{id}", response_model=PedidosEntitySchema)
async def get_pedidosentity(
    id: UUID,
    repository: PedidosEntityRepositoryImpl = Depends(get_pedidosentity_repository)
):
    """Busca PedidosEntity por ID."""
    use_case = GetPedidosEntityByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="PedidosEntity não encontrado")
    return PedidosEntitySchema.from_orm(entity)


@router.put("/pedidosentitys/{id}", response_model=PedidosEntitySchema)
async def update_pedidosentity(
    id: UUID,
    data: UpdatePedidosEntityDTO,
    repository: PedidosEntityRepositoryImpl = Depends(get_pedidosentity_repository)
):
    """Atualiza PedidosEntity."""
    use_case = UpdatePedidosEntityUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="PedidosEntity não encontrado")
    return PedidosEntitySchema.from_orm(entity)


@router.delete("/pedidosentitys/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pedidosentity(
    id: UUID,
    repository: PedidosEntityRepositoryImpl = Depends(get_pedidosentity_repository)
):
    """Deleta PedidosEntity."""
    use_case = DeletePedidosEntityUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="PedidosEntity não encontrado")
