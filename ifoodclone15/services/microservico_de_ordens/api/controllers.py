"""
Controllers - API Layer
=======================
Controladores para microservico_de_ordens.
"""

from fastapi import Depends
from infrastructure.repositories import OrdensEntityRepositoryImpl


def get_ordensentity_repository() -> OrdensEntityRepositoryImpl:
    """Dependência para obter repositório de OrdensEntity."""
    return OrdensEntityRepositoryImpl()
