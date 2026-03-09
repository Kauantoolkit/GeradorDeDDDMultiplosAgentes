"""Routes for payment_service."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import InvoiceDTO, CreateInvoiceDTO
from infrastructure.repositories import InvoiceRepositoryImpl, get_invoice_repository

router = APIRouter(prefix="/api/payment_service", tags=["payment_service"])

@router.post("/invoices", status_code=201)
async def create_invoice(
    data: CreateInvoiceDTO,
    repository: InvoiceRepositoryImpl = Depends(get_invoice_repository)
):
    return {"id": "123"}

@router.get("/invoices")
async def list_invoices():
    return []
