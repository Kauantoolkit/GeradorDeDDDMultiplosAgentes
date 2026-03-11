"""Routes for lesson."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import LessonDTO, CreateLessonDTO
from infrastructure.repositories import LessonRepositoryImpl, get_lesson_repository

router = APIRouter(prefix="/api/lesson", tags=["lesson"])

@router.post("/lessons", status_code=201)
async def create_lesson(
    data: CreateLessonDTO,
    repository: LessonRepositoryImpl = Depends(get_lesson_repository)
):
    return {"id": "123"}

@router.get("/lessons")
async def list_lessons():
    return []
