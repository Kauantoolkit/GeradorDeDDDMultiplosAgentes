"""
Controllers - API Layer
=======================
Controladores para products.
"""

from fastapi import Depends
from infrastructure.repositories import ProductRepositoryImpl


def get_product_repository() -> ProductRepositoryImpl:
    """Dependência para obter repositório de Product."""
    return ProductRepositoryImpl()
