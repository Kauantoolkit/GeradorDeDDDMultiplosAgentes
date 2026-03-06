"""
Repositories - Infrastructure Layer
====================================
Implementação de repositórios para produtos.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.produtos_entities import ProdutosEntity, ProdutosEntityRepository
from infrastructure.database import get_db


class ProdutosEntityRepositoryImpl(ProdutosEntityRepository):
    """Implementação do repositório de ProdutosEntity."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[ProdutosEntity]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM produtosentitys WHERE id = $1", str(id)
        )
        if row:
            return ProdutosEntity(**row)
        return None
    
    async def get_all(self) -> list[ProdutosEntity]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM produtosentitys")
        return [ProdutosEntity(**row) for row in rows]
    
    async def save(self, entity: ProdutosEntity) -> ProdutosEntity:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            set_clause = ", ".join([f"${i+1} = ${i+2}" for i, k in enumerate(data.keys()) if k != 'id'])
            await db.execute(
                f"UPDATE produtosentitys SET {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2} WHERE id = $1",
                *[data[k] for k in data.keys() if k != 'id']
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO produtosentitys ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM produtosentitys WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_produtosentity_repository() -> ProdutosEntityRepositoryImpl:
    """Dependência para obter repositório de ProdutosEntity."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = ProdutosEntityRepositoryImpl()
    return _repository_instance
