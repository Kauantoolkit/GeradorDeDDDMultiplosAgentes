"""Routes for academia_payments."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import PaymentDTO, CreatePaymentDTO
from infrastructure.repositories import PaymentRepositoryImpl, get_payment_repository

router = APIRouter(prefix="/api/academia_payments", tags=["academia_payments"])

@router.post("/payments", status_code=201)
async def create_payment(
    data: CreatePaymentDTO,
    repository: PaymentRepositoryImpl = Depends(get_payment_repository)
):
    return {"id": "123"}

@router.get("/payments")
async def list_payments():
    return []
