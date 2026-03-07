"""
Controllers - API Layer
=======================
Controladores para customer_service.
"""

from fastapi import Depends
from infrastructure.repositories import CustomerRepositoryImpl


def get_customer_repository() -> CustomerRepositoryImpl:
    """Dependência para obter repositório de Customer."""
    return CustomerRepositoryImpl()
