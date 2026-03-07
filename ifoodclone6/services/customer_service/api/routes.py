"""
Routes - API Layer
==================
Definição de rotas para customer_service.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import CustomerDTO, CreateCustomerDTO, UpdateCustomerDTO
from application.use_cases import (
    CreateCustomerUseCase,
    GetCustomerByIdUseCase,
    UpdateCustomerUseCase,
    DeleteCustomerUseCase,
)
from infrastructure.repositories import CustomerRepositoryImpl
from api.schemas import CustomerSchema, CreateCustomerSchema
from api.controllers import get_customer_repository


router = APIRouter(prefix="/api/customer_service", tags=["customer_service"])


@router.post("/customers", response_model=CustomerSchema, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CreateCustomerSchema,
    repository: CustomerRepositoryImpl = Depends(get_customer_repository)
):
    """Cria um novo Customer."""
    use_case = CreateCustomerUseCase(repository)
    entity = await use_case.execute(data.dict())
    return CustomerSchema.from_orm(entity)


@router.get("/customers", response_model=List[CustomerSchema])
async def list_customers(
    repository: CustomerRepositoryImpl = Depends(get_customer_repository)
):
    """Lista todos os Customers."""
    entities = await repository.get_all()
    return [CustomerSchema.from_orm(e) for e in entities]


@router.get("/customers/{id}", response_model=CustomerSchema)
async def get_customer(
    id: UUID,
    repository: CustomerRepositoryImpl = Depends(get_customer_repository)
):
    """Busca Customer por ID."""
    use_case = GetCustomerByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"{Customer} não encontrado")
    return CustomerSchema.from_orm(entity)


@router.put("/customers/{id}", response_model=CustomerSchema)
async def update_customer(
    id: UUID,
    data: UpdateCustomerDTO,
    repository: CustomerRepositoryImpl = Depends(get_customer_repository)
):
    """Atualiza Customer."""
    use_case = UpdateCustomerUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail=f"{Customer} não encontrado")
    return CustomerSchema.from_orm(entity)


@router.delete("/customers/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    id: UUID,
    repository: CustomerRepositoryImpl = Depends(get_customer_repository)
):
    """Deleta Customer."""
    use_case = DeleteCustomerUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail=f"{Customer} não encontrado")
