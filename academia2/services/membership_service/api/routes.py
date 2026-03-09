"""Routes for membership_service."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import MemberDTO, CreateMemberDTO
from infrastructure.repositories import MemberRepositoryImpl, get_member_repository

router = APIRouter(prefix="/api/membership_service", tags=["membership_service"])

@router.post("/members", status_code=201)
async def create_member(
    data: CreateMemberDTO,
    repository: MemberRepositoryImpl = Depends(get_member_repository)
):
    return {"id": "123"}

@router.get("/members")
async def list_members():
    return []
