"""Routes for academia."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import UserDTO, CreateUserDTO
from infrastructure.repositories import UserRepositoryImpl, get_user_repository

router = APIRouter(prefix="/api/academia", tags=["academia"])

@router.post("/users", status_code=201)
async def create_user(
    data: CreateUserDTO,
    repository: UserRepositoryImpl = Depends(get_user_repository)
):
    return {"id": "123"}

@router.get("/users")
async def list_users():
    return []
