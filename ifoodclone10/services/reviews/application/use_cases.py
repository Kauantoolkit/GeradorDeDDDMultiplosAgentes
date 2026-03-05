"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio reviews.
"""

from uuid import UUID
from domain.reviews_entities import Review


class CreateReviewUseCase:
    """Use case para criar Review."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Review:
        entity = Review.create(**data)
        return await self.repository.save(entity)


class GetReviewByIdUseCase:
    """Use case para buscar Review por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Review | None:
        return await self.repository.get_by_id(id)


class UpdateReviewUseCase:
    """Use case para atualizar Review."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> Review | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteReviewUseCase:
    """Use case para deletar Review."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
