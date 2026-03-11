"""Repositories for auth."""
from uuid import UUID
from typing import Optional
from domain.auth_entities import Usuario, UsuarioRepository

class UsuarioRepositoryImpl(UsuarioRepository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[Usuario]:
        pass
    
    async def get_all(self) -> list[Usuario]:
        pass
    
    async def save(self, entity: Usuario) -> Usuario:
        return entity

_repository_instance = None

def get_usuario_repository() -> UsuarioRepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = UsuarioRepositoryImpl()
    return _repository_instance
