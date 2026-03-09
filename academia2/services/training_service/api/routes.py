"""Routes for training_service."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import SessionDTO, CreateSessionDTO
from infrastructure.repositories import SessionRepositoryImpl, get_session_repository

router = APIRouter(prefix="/api/training_service", tags=["training_service"])

@router.post("/sessions", status_code=201)
async def create_session(
    data: CreateSessionDTO,
    repository: SessionRepositoryImpl = Depends(get_session_repository)
):
    return {"id": "123"}

@router.get("/sessions")
async def list_sessions():
    return []
