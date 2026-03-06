"""
Controllers - API Layer
=======================
Controladores para ifoodclone17_application.
"""

from fastapi import Depends
from infrastructure.repositories import OrderserviceRepositoryImpl


def get_orderservice_repository() -> OrderserviceRepositoryImpl:
    """Dependência para obter repositório de Orderservice."""
    return OrderserviceRepositoryImpl()
