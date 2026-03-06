"""
Controllers - API Layer
=======================
Controladores para users.
"""

from fastapi import Depends
from infrastructure.repositories import UserRepositoryImpl


def get_user_repository() -> UserRepositoryImpl:
    """Dependência para obter repositório de User."""
    return UserRepositoryImpl()
