"""
Repositories - Infrastructure Layer
====================================
Implementação de repositórios para payment.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.payment_entities import Payment, PaymentRepository
from infrastructure.database import get_db


class PaymentRepositoryImpl(PaymentRepository):
    """Implementação do repositório de Payment."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[Payment]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM payments WHERE id = $1", str(id)
        )
        if row:
            return Payment(**row)
        return None
    
    async def get_all(self) -> list[Payment]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM payments")
        return [Payment(**row) for row in rows]
    
    async def save(self, entity: Payment) -> Payment:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            set_clause = ", ".join([f"${i+1} = ${i+2}" for i, k in enumerate(data.keys()) if k != 'id'])
            await db.execute(
                f"UPDATE payments SET {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2} WHERE id = $1",
                *[data[k] for k in data.keys() if k != 'id']
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO payments ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM payments WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_payment_repository() -> PaymentRepositoryImpl:
    """Dependência para obter repositório de Payment."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = PaymentRepositoryImpl()
    return _repository_instance
