"""
Repositories - Infrastructure Layer
====================================
Implementação de repositórios para notification.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.notification_entities import Notification, NotificationRepository
from infrastructure.database import get_db


class NotificationRepositoryImpl(NotificationRepository):
    """Implementação do repositório de Notification."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[Notification]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM notifications WHERE id = $1", str(id)
        )
        if row:
            return Notification(**row)
        return None
    
    async def get_all(self) -> list[Notification]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM notifications")
        return [Notification(**row) for row in rows]
    
    async def save(self, entity: Notification) -> Notification:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            set_clause = ", ".join([f"${i+1} = ${i+2}" for i, k in enumerate(data.keys()) if k != 'id'])
            await db.execute(
                f"UPDATE notifications SET {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2} WHERE id = $1",
                *[data[k] for k in data.keys() if k != 'id']
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO notifications ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM notifications WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_notification_repository() -> NotificationRepositoryImpl:
    """Dependência para obter repositório de Notification."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = NotificationRepositoryImpl()
    return _repository_instance
