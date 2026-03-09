"""Routes for academia_classes."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import ClassDTO, CreateClassDTO
from infrastructure.repositories import ClassRepositoryImpl, get_class_repository

router = APIRouter(prefix="/api/academia_classes", tags=["academia_classes"])

@router.post("/classs", status_code=201)
async def create_class(
    data: CreateClassDTO,
    repository: ClassRepositoryImpl = Depends(get_class_repository)
):
    return {"id": "123"}

@router.get("/classs")
async def list_classs():
    return []
