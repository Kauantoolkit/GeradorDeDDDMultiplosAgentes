"""
Repositories - Infrastructure Layer
====================================
Implementação de repositórios para ifoodclone17_infrastructure.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.ifoodclone17_infrastructure_entities import Database, DatabaseRepository
from infrastructure.database import get_db


class DatabaseRepositoryImpl(DatabaseRepository):
    """Implementação do repositório de Database."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[Database]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM databases WHERE id = $1", str(id)
        )
        if row:
            return Database(**row)
        return None
    
    async def get_all(self) -> list[Database]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM databases")
        return [Database(**row) for row in rows]
    
    async def save(self, entity: Database) -> Database:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            set_clause = ", ".join([f"${i+1} = ${i+2}" for i, k in enumerate(data.keys()) if k != 'id'])
            await db.execute(
                f"UPDATE databases SET {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2} WHERE id = $1",
                *[data[k] for k in data.keys() if k != 'id']
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO databases ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM databases WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_database_repository() -> DatabaseRepositoryImpl:
    """Dependência para obter repositório de Database."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = DatabaseRepositoryImpl()
    return _repository_instance
