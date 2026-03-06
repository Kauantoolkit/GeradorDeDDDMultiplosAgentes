"""
Routes - API Layer
==================
Definição de rotas para products.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import ProductDTO, CreateProductDTO, UpdateProductDTO
from application.use_cases import (
    CreateProductUseCase,
    GetProductByIdUseCase,
    UpdateProductUseCase,
    DeleteProductUseCase,
)
from infrastructure.repositories import ProductRepositoryImpl
from api.schemas import ProductSchema, CreateProductSchema
from api.controllers import get_product_repository


router = APIRouter(prefix="/api/products", tags=["products"])


@router.post("/products", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: CreateProductSchema,
    repository: ProductRepositoryImpl = Depends(get_product_repository)
):
    """Cria um novo Product."""
    use_case = CreateProductUseCase(repository)
    entity = await use_case.execute(data.dict())
    return ProductSchema.from_orm(entity)


@router.get("/products", response_model=List[ProductSchema])
async def list_products(
    repository: ProductRepositoryImpl = Depends(get_product_repository)
):
    """Lista todos os Products."""
    entities = await repository.get_all()
    return [ProductSchema.from_orm(e) for e in entities]


@router.get("/products/{id}", response_model=ProductSchema)
async def get_product(
    id: UUID,
    repository: ProductRepositoryImpl = Depends(get_product_repository)
):
    """Busca Product por ID."""
    use_case = GetProductByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="Product não encontrado")
    return ProductSchema.from_orm(entity)


@router.put("/products/{id}", response_model=ProductSchema)
async def update_product(
    id: UUID,
    data: UpdateProductDTO,
    repository: ProductRepositoryImpl = Depends(get_product_repository)
):
    """Atualiza Product."""
    use_case = UpdateProductUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="Product não encontrado")
    return ProductSchema.from_orm(entity)


@router.delete("/products/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    id: UUID,
    repository: ProductRepositoryImpl = Depends(get_product_repository)
):
    """Deleta Product."""
    use_case = DeleteProductUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="Product não encontrado")
