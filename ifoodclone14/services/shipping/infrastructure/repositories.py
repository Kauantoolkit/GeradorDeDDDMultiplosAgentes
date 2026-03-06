"""
Repositories - Infrastructure Layer
====================================
Implementação de repositórios para shipping.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.shipping_entities import Address, AddressRepository
from infrastructure.database import get_db


class AddressRepositoryImpl(AddressRepository):
    """Implementação do repositório de Address."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[Address]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM addresss WHERE id = $1", str(id)
        )
        if row:
            return Address(**row)
        return None
    
    async def get_all(self) -> list[Address]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM addresss")
        return [Address(**row) for row in rows]
    
    async def save(self, entity: Address) -> Address:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            set_clause = ", ".join([f"${i+1} = ${i+2}" for i, k in enumerate(data.keys()) if k != 'id'])
            await db.execute(
                f"UPDATE addresss SET {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2} WHERE id = $1",
                *[data[k] for k in data.keys() if k != 'id']
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO addresss ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM addresss WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_address_repository() -> AddressRepositoryImpl:
    """Dependência para obter repositório de Address."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = AddressRepositoryImpl()
    return _repository_instance
