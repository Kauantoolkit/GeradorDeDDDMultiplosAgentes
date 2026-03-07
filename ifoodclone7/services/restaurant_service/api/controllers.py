"""
Controllers - API Layer
=======================
Controladores para restaurant_service.
"""

from fastapi import Depends
from infrastructure.repositories import RestaurantRepositoryImpl


def get_restaurant_repository() -> RestaurantRepositoryImpl:
    """Dependência para obter repositório de Restaurant."""
    return RestaurantRepositoryImpl()
