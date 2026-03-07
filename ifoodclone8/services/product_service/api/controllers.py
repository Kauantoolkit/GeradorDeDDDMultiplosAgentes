"""
Controllers - API Layer
=======================
Controladores para product_service.
"""

from fastapi import Depends
from infrastructure.repositories import ProductRepositoryImpl


def get_product_repository() -> ProductRepositoryImpl:
    """Dependência para obter repositório de Product."""
    return ProductRepositoryImpl()
