"""Routes for academia_auth."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import UsuarioDTO, CreateUsuarioDTO
from infrastructure.repositories import UsuarioRepositoryImpl, get_usuario_repository

router = APIRouter(prefix="/api/academia_auth", tags=["academia_auth"])

@router.post("/usuarios", status_code=201)
async def create_usuario(
    data: CreateUsuarioDTO,
    repository: UsuarioRepositoryImpl = Depends(get_usuario_repository)
):
    return {"id": "123"}

@router.get("/usuarios")
async def list_usuarios():
    return []
