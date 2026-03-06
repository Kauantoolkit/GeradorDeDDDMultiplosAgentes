"""
Repositories - Infrastructure Layer
====================================
Implementação de repositórios para ifoodclone17_application.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.ifoodclone17_application_entities import Orderservice, OrderserviceRepository
from infrastructure.database import get_db


class OrderserviceRepositoryImpl(OrderserviceRepository):
    """Implementação do repositório de Orderservice."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[Orderservice]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM orderservices WHERE id = $1", str(id)
        )
        if row:
            return Orderservice(**row)
        return None
    
    async def get_all(self) -> list[Orderservice]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM orderservices")
        return [Orderservice(**row) for row in rows]
    
    async def save(self, entity: Orderservice) -> Orderservice:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            set_clause = ", ".join([f"${i+1} = ${i+2}" for i, k in enumerate(data.keys()) if k != 'id'])
            await db.execute(
                f"UPDATE orderservices SET {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2} WHERE id = $1",
                *[data[k] for k in data.keys() if k != 'id']
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO orderservices ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM orderservices WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_orderservice_repository() -> OrderserviceRepositoryImpl:
    """Dependência para obter repositório de Orderservice."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = OrderserviceRepositoryImpl()
    return _repository_instance
