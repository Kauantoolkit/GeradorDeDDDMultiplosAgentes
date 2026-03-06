"""
Repositories - Infrastructure Layer
====================================
Implementação de repositórios para ifoodclone17_api.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.ifoodclone17_api_entities import Ordercontroller, OrdercontrollerRepository
from infrastructure.database import get_db


class OrdercontrollerRepositoryImpl(OrdercontrollerRepository):
    """Implementação do repositório de Ordercontroller."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[Ordercontroller]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM ordercontrollers WHERE id = $1", str(id)
        )
        if row:
            return Ordercontroller(**row)
        return None
    
    async def get_all(self) -> list[Ordercontroller]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM ordercontrollers")
        return [Ordercontroller(**row) for row in rows]
    
    async def save(self, entity: Ordercontroller) -> Ordercontroller:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            set_clause = ", ".join([f"${i+1} = ${i+2}" for i, k in enumerate(data.keys()) if k != 'id'])
            await db.execute(
                f"UPDATE ordercontrollers SET {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2} WHERE id = $1",
                *[data[k] for k in data.keys() if k != 'id']
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO ordercontrollers ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM ordercontrollers WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_ordercontroller_repository() -> OrdercontrollerRepositoryImpl:
    """Dependência para obter repositório de Ordercontroller."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = OrdercontrollerRepositoryImpl()
    return _repository_instance
