"""
Controllers - API Layer
=======================
Controladores para microservico_de_produtos.
"""

from fastapi import Depends
from infrastructure.repositories import ProdutosEntityRepositoryImpl


def get_produtosentity_repository() -> ProdutosEntityRepositoryImpl:
    """Dependência para obter repositório de ProdutosEntity."""
    return ProdutosEntityRepositoryImpl()
