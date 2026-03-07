
"""Repositories - Infrastructure Layer
====================================
Implementação de repositórios para customer.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.customer_entities import Customer, CustomerRepository
from infrastructure.database import get_db


class CustomerRepositoryImpl(CustomerRepository):
    """Implementação do repositório de Customer."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[Customer]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM customers WHERE id = $1", str(id)
        )
        if row:
            return Customer(**row)
        return None
    
    async def get_all(self) -> list[Customer]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM customers")
        return [Customer(**row) for row in rows]
    
    async def save(self, entity: Customer) -> Customer:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            columns = [k for k in data.keys() if k != 'id']
            set_clause = ", ".join([f"{c} = ${i+2}" for i, c in enumerate(columns)])
            await db.execute(
                f"UPDATE customers SET {set_clause} WHERE id = $1",
                *[data[c] for c in columns]
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO customers ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM customers WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_customer_repository() -> CustomerRepositoryImpl:
    """Dependência para obter repositório de Customer."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = CustomerRepositoryImpl()
    return _repository_instance
