"""Routes for users."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import EntityDTO, CreateEntityDTO
from infrastructure.repositories import EntityRepositoryImpl, get_entity_repository

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/entitys", status_code=201)
async def create_entity(
    data: CreateEntityDTO,
    repository: EntityRepositoryImpl = Depends(get_entity_repository)
):
    return {"id": "123"}

@router.get("/entitys")
async def list_entitys():
    return []
