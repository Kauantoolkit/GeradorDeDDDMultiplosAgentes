"""Routes for instructor."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import InstructorDTO, CreateInstructorDTO
from infrastructure.repositories import InstructorRepositoryImpl, get_instructor_repository

router = APIRouter(prefix="/api/instructor", tags=["instructor"])

@router.post("/instructors", status_code=201)
async def create_instructor(
    data: CreateInstructorDTO,
    repository: InstructorRepositoryImpl = Depends(get_instructor_repository)
):
    return {"id": "123"}

@router.get("/instructors")
async def list_instructors():
    return []
