"""
Controllers - API Layer
=======================
Controladores para shipping.
"""

from fastapi import Depends
from infrastructure.repositories import AddressRepositoryImpl


def get_address_repository() -> AddressRepositoryImpl:
    """Dependência para obter repositório de Address."""
    return AddressRepositoryImpl()
