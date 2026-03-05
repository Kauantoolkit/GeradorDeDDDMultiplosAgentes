"""
Routes - API Layer
==================
Definição de rotas para payment_service.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import PaymentDTO, CreatePaymentDTO, UpdatePaymentDTO
from application.use_cases import (
    CreatePaymentUseCase,
    GetPaymentByIdUseCase,
    UpdatePaymentUseCase,
    DeletePaymentUseCase,
)
from infrastructure.repositories import PaymentRepositoryImpl
from api.schemas import PaymentSchema, CreatePaymentSchema
from api.controllers import get_payment_repository


router = APIRouter(prefix="/api/payment_service", tags=["payment_service"])


@router.post("/payments", response_model=PaymentSchema, status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: CreatePaymentSchema,
    repository: PaymentRepositoryImpl = Depends(get_payment_repository)
):
    """Cria um novo Payment."""
    use_case = CreatePaymentUseCase(repository)
    entity = await use_case.execute(data.dict())
    return PaymentSchema.from_orm(entity)


@router.get("/payments", response_model=List[PaymentSchema])
async def list_payments(
    repository: PaymentRepositoryImpl = Depends(get_payment_repository)
):
    """Lista todos os Payments."""
    entities = await repository.get_all()
    return [PaymentSchema.from_orm(e) for e in entities]


@router.get("/payments/{id}", response_model=PaymentSchema)
async def get_payment(
    id: UUID,
    repository: PaymentRepositoryImpl = Depends(get_payment_repository)
):
    """Busca Payment por ID."""
    use_case = GetPaymentByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="Payment não encontrado")
    return PaymentSchema.from_orm(entity)


@router.put("/payments/{id}", response_model=PaymentSchema)
async def update_payment(
    id: UUID,
    data: UpdatePaymentDTO,
    repository: PaymentRepositoryImpl = Depends(get_payment_repository)
):
    """Atualiza Payment."""
    use_case = UpdatePaymentUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="Payment não encontrado")
    return PaymentSchema.from_orm(entity)


@router.delete("/payments/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    id: UUID,
    repository: PaymentRepositoryImpl = Depends(get_payment_repository)
):
    """Deleta Payment."""
    use_case = DeletePaymentUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="Payment não encontrado")
