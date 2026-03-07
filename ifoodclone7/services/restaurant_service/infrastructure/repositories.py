
"""Repositories - Infrastructure Layer
====================================
Implementação de repositórios para restaurant.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.restaurant_entities import Restaurant, RestaurantRepository
from infrastructure.database import get_db


class RestaurantRepositoryImpl(RestaurantRepository):
    """Implementação do repositório de Restaurant."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[Restaurant]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM restaurants WHERE id = $1", str(id)
        )
        if row:
            return Restaurant(**row)
        return None
    
    async def get_all(self) -> list[Restaurant]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM restaurants")
        return [Restaurant(**row) for row in rows]
    
    async def save(self, entity: Restaurant) -> Restaurant:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            columns = [k for k in data.keys() if k != 'id']
            set_clause = ", ".join([f"{c} = ${i+2}" for i, c in enumerate(columns)])
            await db.execute(
                f"UPDATE restaurants SET {set_clause} WHERE id = $1",
                *[data[c] for c in columns]
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO restaurants ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM restaurants WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_restaurant_repository() -> RestaurantRepositoryImpl:
    """Dependência para obter repositório de Restaurant."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = RestaurantRepositoryImpl()
    return _repository_instance
