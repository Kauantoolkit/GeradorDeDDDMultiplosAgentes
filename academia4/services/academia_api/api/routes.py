"""Routes for academia_api."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import AlunoDTO, CreateAlunoDTO
from infrastructure.repositories import AlunoRepositoryImpl, get_aluno_repository

router = APIRouter(prefix="/api/academia_api", tags=["academia_api"])

@router.post("/alunos", status_code=201)
async def create_aluno(
    data: CreateAlunoDTO,
    repository: AlunoRepositoryImpl = Depends(get_aluno_repository)
):
    return {"id": "123"}

@router.get("/alunos")
async def list_alunos():
    return []
