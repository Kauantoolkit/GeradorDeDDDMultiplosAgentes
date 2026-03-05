"""
Routes - API Layer
==================
Definição de rotas para reviews.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from application.dtos import ReviewDTO, CreateReviewDTO, UpdateReviewDTO
from application.use_cases import (
    CreateReviewUseCase,
    GetReviewByIdUseCase,
    UpdateReviewUseCase,
    DeleteReviewUseCase,
)
from infrastructure.repositories import ReviewRepositoryImpl
from api.schemas import ReviewSchema, CreateReviewSchema
from api.controllers import get_review_repository


router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.post("/reviews", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    data: CreateReviewSchema,
    repository: ReviewRepositoryImpl = Depends(get_review_repository)
):
    """Cria um novo Review."""
    use_case = CreateReviewUseCase(repository)
    entity = await use_case.execute(data.dict())
    return ReviewSchema.from_orm(entity)


@router.get("/reviews", response_model=List[ReviewSchema])
async def list_reviews(
    repository: ReviewRepositoryImpl = Depends(get_review_repository)
):
    """Lista todos os Reviews."""
    entities = await repository.get_all()
    return [ReviewSchema.from_orm(e) for e in entities]


@router.get("/reviews/{id}", response_model=ReviewSchema)
async def get_review(
    id: UUID,
    repository: ReviewRepositoryImpl = Depends(get_review_repository)
):
    """Busca Review por ID."""
    use_case = GetReviewByIdUseCase(repository)
    entity = await use_case.execute(id)
    if not entity:
        raise HTTPException(status_code=404, detail="Review não encontrado")
    return ReviewSchema.from_orm(entity)


@router.put("/reviews/{id}", response_model=ReviewSchema)
async def update_review(
    id: UUID,
    data: UpdateReviewDTO,
    repository: ReviewRepositoryImpl = Depends(get_review_repository)
):
    """Atualiza Review."""
    use_case = UpdateReviewUseCase(repository)
    entity = await use_case.execute(id, data.dict(exclude_unset=True))
    if not entity:
        raise HTTPException(status_code=404, detail="Review não encontrado")
    return ReviewSchema.from_orm(entity)


@router.delete("/reviews/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    id: UUID,
    repository: ReviewRepositoryImpl = Depends(get_review_repository)
):
    """Deleta Review."""
    use_case = DeleteReviewUseCase(repository)
    result = await use_case.execute(id)
    if not result:
        raise HTTPException(status_code=404, detail="Review não encontrado")
