"""
Controllers - API Layer
=======================
Controladores para microservico_de_usuarios.
"""

from fastapi import Depends
from infrastructure.repositories import UsuariosEntityRepositoryImpl


def get_usuariosentity_repository() -> UsuariosEntityRepositoryImpl:
    """Dependência para obter repositório de UsuariosEntity."""
    return UsuariosEntityRepositoryImpl()
