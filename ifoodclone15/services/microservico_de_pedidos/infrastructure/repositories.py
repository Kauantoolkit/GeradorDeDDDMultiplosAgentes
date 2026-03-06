"""
Repositories - Infrastructure Layer
====================================
Implementação de repositórios para pedidos.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.pedidos_entities import PedidosEntity, PedidosEntityRepository
from infrastructure.database import get_db


class PedidosEntityRepositoryImpl(PedidosEntityRepository):
    """Implementação do repositório de PedidosEntity."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[PedidosEntity]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM pedidosentitys WHERE id = $1", str(id)
        )
        if row:
            return PedidosEntity(**row)
        return None
    
    async def get_all(self) -> list[PedidosEntity]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM pedidosentitys")
        return [PedidosEntity(**row) for row in rows]
    
    async def save(self, entity: PedidosEntity) -> PedidosEntity:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            set_clause = ", ".join([f"${i+1} = ${i+2}" for i, k in enumerate(data.keys()) if k != 'id'])
            await db.execute(
                f"UPDATE pedidosentitys SET {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2} WHERE id = $1",
                *[data[k] for k in data.keys() if k != 'id']
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO pedidosentitys ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM pedidosentitys WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_pedidosentity_repository() -> PedidosEntityRepositoryImpl:
    """Dependência para obter repositório de PedidosEntity."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = PedidosEntityRepositoryImpl()
    return _repository_instance
