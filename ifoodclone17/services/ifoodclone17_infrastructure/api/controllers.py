"""
Controllers - API Layer
=======================
Controladores para ifoodclone17_infrastructure.
"""

from fastapi import Depends
from infrastructure.repositories import DatabaseRepositoryImpl


def get_database_repository() -> DatabaseRepositoryImpl:
    """Dependência para obter repositório de Database."""
    return DatabaseRepositoryImpl()
