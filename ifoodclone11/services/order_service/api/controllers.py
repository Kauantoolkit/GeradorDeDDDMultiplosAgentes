"""
Controllers - API Layer
=======================
Controladores para order_service.
"""

from fastapi import Depends
from infrastructure.repositories import OrderRepositoryImpl


def get_order_repository() -> OrderRepositoryImpl:
    """Dependência para obter repositório de Order."""
    return OrderRepositoryImpl()
