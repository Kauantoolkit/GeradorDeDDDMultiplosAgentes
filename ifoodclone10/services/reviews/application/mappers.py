"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import ReviewDTO, CreateReviewDTO
from domain.reviews_entities import Review


class ReviewMapper:
    """Mapper para Review."""
    
    @staticmethod
    def to_dto(entity: Review) -> ReviewDTO:
        return ReviewDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: ReviewDTO) -> Review:
        return Review(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateReviewDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
