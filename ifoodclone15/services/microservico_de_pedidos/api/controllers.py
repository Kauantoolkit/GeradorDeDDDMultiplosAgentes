"""
Controllers - API Layer
=======================
Controladores para microservico_de_pedidos.
"""

from fastapi import Depends
from infrastructure.repositories import PedidosEntityRepositoryImpl


def get_pedidosentity_repository() -> PedidosEntityRepositoryImpl:
    """Dependência para obter repositório de PedidosEntity."""
    return PedidosEntityRepositoryImpl()
