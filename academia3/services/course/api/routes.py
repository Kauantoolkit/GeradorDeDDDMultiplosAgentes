"""Routes for course."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import CourseDTO, CreateCourseDTO
from infrastructure.repositories import CourseRepositoryImpl, get_course_repository

router = APIRouter(prefix="/api/course", tags=["course"])

@router.post("/courses", status_code=201)
async def create_course(
    data: CreateCourseDTO,
    repository: CourseRepositoryImpl = Depends(get_course_repository)
):
    return {"id": "123"}

@router.get("/courses")
async def list_courses():
    return []
