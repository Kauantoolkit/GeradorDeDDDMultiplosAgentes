"""
Controllers - API Layer
=======================
Controladores para ifoodclone17_api.
"""

from fastapi import Depends
from infrastructure.repositories import OrdercontrollerRepositoryImpl


def get_ordercontroller_repository() -> OrdercontrollerRepositoryImpl:
    """Dependência para obter repositório de Ordercontroller."""
    return OrdercontrollerRepositoryImpl()
