"""
Routes - API Layer
==================
Definição de rotas para microservico_de_produtos.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import ProdutosEntityDTO, CreateProdutosEntityDTO, UpdateProdutosEntityDTO
from application.use_cases import (
    CreateProdutosEntityUseCase,
    GetProdutosEntityByIdUseCase,
    UpdateProdutosEntityUseCase,
    DeleteProdutosEntityUseCase,
)
from infrastructure.repositories import ProdutosEntityRepositoryImpl
from api.schemas import ProdutosEntitySchema, CreateProdutosEntitySchema
from api.controllers import get_produtosentity_repository


router = APIRouter(prefix="/api/microservico_de_produtos", tags=["microservico_de_produtos"])


@router.post("/produtosentitys", response_model=ProdutosEntitySchema, status_code=status.HTTP_201_CREATED)
async def create_produtosentity(
    data: CreateProdutosEntitySchema,
    repository: ProdutosEntityRepositoryImpl = Depends(get_produtosentity_repository)
):
    """Cria um novo ProdutosEntity."""
    use_case = CreateProdutosEntityUseCase(repository)
    entity = await use_case.execute(data.dict())
    return ProdutosEntitySchema.from_orm(entity)


@router.get("/produtosentitys", response_model=List[ProdutosEntitySchema])
async def list_produtosentitys(
    repository: ProdutosEntityRepositoryImpl = Depends(get_produtosentity_repository)
):
    """Lista todos os ProdutosEntitys."""
    entities = await repository.get_all()
    return [ProdutosEntitySchema.from_orm(e) for e in entities]


@router.get("/produtosentitys/{id}", response_model=ProdutosEntitySchema)
async def get_produtosentity(
    id: UUID,
    repository: ProdutosEntityRepositoryImpl = Depends(get_produtosentity_repository)
):
    """Busca ProdutosEntity por ID."""
    use_case = GetProdutosEntityByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="ProdutosEntity não encontrado")
    return ProdutosEntitySchema.from_orm(entity)


@router.put("/produtosentitys/{id}", response_model=ProdutosEntitySchema)
async def update_produtosentity(
    id: UUID,
    data: UpdateProdutosEntityDTO,
    repository: ProdutosEntityRepositoryImpl = Depends(get_produtosentity_repository)
):
    """Atualiza ProdutosEntity."""
    use_case = UpdateProdutosEntityUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="ProdutosEntity não encontrado")
    return ProdutosEntitySchema.from_orm(entity)


@router.delete("/produtosentitys/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_produtosentity(
    id: UUID,
    repository: ProdutosEntityRepositoryImpl = Depends(get_produtosentity_repository)
):
    """Deleta ProdutosEntity."""
    use_case = DeleteProdutosEntityUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="ProdutosEntity não encontrado")
