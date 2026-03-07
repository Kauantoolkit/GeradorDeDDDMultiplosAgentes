"""
Controllers - API Layer
=======================
Controladores para delivery_service.
"""

from fastapi import Depends
from infrastructure.repositories import DeliveryRepositoryImpl


def get_delivery_repository() -> DeliveryRepositoryImpl:
    """Dependência para obter repositório de Delivery."""
    return DeliveryRepositoryImpl()
