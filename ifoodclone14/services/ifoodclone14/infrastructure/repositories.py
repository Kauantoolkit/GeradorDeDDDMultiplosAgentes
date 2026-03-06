"""
Repositories - Infrastructure Layer
====================================
Implementação de repositórios para ifoodclone14.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.ifoodclone14_entities import User, UserRepository
from infrastructure.database import get_db


class UserRepositoryImpl(UserRepository):
    """Implementação do repositório de User."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[User]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM users WHERE id = $1", str(id)
        )
        if row:
            return User(**row)
        return None
    
    async def get_all(self) -> list[User]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM users")
        return [User(**row) for row in rows]
    
    async def save(self, entity: User) -> User:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            set_clause = ", ".join([f"${i+1} = ${i+2}" for i, k in enumerate(data.keys()) if k != 'id'])
            await db.execute(
                f"UPDATE users SET {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2} WHERE id = $1",
                *[data[k] for k in data.keys() if k != 'id']
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO users ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM users WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_user_repository() -> UserRepositoryImpl:
    """Dependência para obter repositório de User."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = UserRepositoryImpl()
    return _repository_instance
