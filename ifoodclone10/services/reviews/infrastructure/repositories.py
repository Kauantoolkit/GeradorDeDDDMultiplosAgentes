"""
Repositories - Infrastructure Layer
====================================
Implementação de repositórios para reviews.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.reviews_entities import Review, ReviewRepository
from infrastructure.database import get_db


class ReviewRepositoryImpl(ReviewRepository):
    """Implementação do repositório de Review."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[Review]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM reviews WHERE id = $1", str(id)
        )
        if row:
            return Review(**row)
        return None
    
    async def get_all(self) -> list[Review]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM reviews")
        return [Review(**row) for row in rows]
    
    async def save(self, entity: Review) -> Review:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            set_clause = ", ".join([f"${i+1} = ${i+2}" for i, k in enumerate(data.keys()) if k != 'id'])
            await db.execute(
                f"UPDATE reviews SET {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2} WHERE id = $1",
                *[data[k] for k in data.keys() if k != 'id']
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO reviews ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM reviews WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_review_repository() -> ReviewRepositoryImpl:
    """Dependência para obter repositório de Review."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = ReviewRepositoryImpl()
    return _repository_instance
