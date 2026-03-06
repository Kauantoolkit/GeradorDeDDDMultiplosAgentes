"""
Repositories - Infrastructure Layer
====================================
Implementação de repositórios para usuarios.
"""

import asyncpg
import os
from uuid import UUID
from typing import Optional
from domain.usuarios_entities import UsuariosEntity, UsuariosEntityRepository
from infrastructure.database import get_db


class UsuariosEntityRepositoryImpl(UsuariosEntityRepository):
    """Implementação do repositório de UsuariosEntity."""
    
    def __init__(self):
        self.db = None
    
    def _get_db(self):
        """Obtém conexão do banco."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return self.db
    
    async def get_by_id(self, id: UUID) -> Optional[UsuariosEntity]:
        db = self._get_db()
        row = await db.fetchrow(
            "SELECT * FROM usuariosentitys WHERE id = $1", str(id)
        )
        if row:
            return UsuariosEntity(**row)
        return None
    
    async def get_all(self) -> list[UsuariosEntity]:
        db = self._get_db()
        rows = await db.fetch("SELECT * FROM usuariosentitys")
        return [UsuariosEntity(**row) for row in rows]
    
    async def save(self, entity: UsuariosEntity) -> UsuariosEntity:
        db = self._get_db()
        data = entity.to_dict()
        
        existing = await self.get_by_id(entity.id)
        if existing:
            # Build dynamic UPDATE query
            set_clause = ", ".join([f"${i+1} = ${i+2}" for i, k in enumerate(data.keys()) if k != 'id'])
            await db.execute(
                f"UPDATE usuariosentitys SET {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2}, {k} = ${i+2} WHERE id = $1",
                *[data[k] for k in data.keys() if k != 'id']
            )
        else:
            columns = ", ".join(data.keys())
            values = ", ".join([f"${i+1}" for i in range(len(data))])
            await db.execute(
                f"INSERT INTO usuariosentitys ({columns}) VALUES ({values})",
                *data.values()
            )
        return entity
    
    async def delete(self, id: UUID) -> bool:
        db = self._get_db()
        result = await db.execute(
            "DELETE FROM usuariosentitys WHERE id = $1", str(id)
        )
        return result != "DELETE 0"


# Instância global do repositório
_repository_instance = None


def get_usuariosentity_repository() -> UsuariosEntityRepositoryImpl:
    """Dependência para obter repositório de UsuariosEntity."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = UsuariosEntityRepositoryImpl()
    return _repository_instance
