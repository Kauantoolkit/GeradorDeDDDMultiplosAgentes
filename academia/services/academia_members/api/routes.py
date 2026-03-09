"""Routes for academia_members."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List

from application.dtos import MemberDTO, CreateMemberDTO
from infrastructure.repositories import MemberRepositoryImpl, get_member_repository

router = APIRouter(prefix="/api/academia_members", tags=["academia_members"])

@router.post("/members", status_code=201)
async def create_member(
    data: CreateMemberDTO,
    repository: MemberRepositoryImpl = Depends(get_member_repository)
):
    return {"id": "123"}

@router.get("/members")
async def list_members():
    return []
