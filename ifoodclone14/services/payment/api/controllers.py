"""
Controllers - API Layer
=======================
Controladores para payment.
"""

from fastapi import Depends
from infrastructure.repositories import PaymentRepositoryImpl


def get_payment_repository() -> PaymentRepositoryImpl:
    """Dependência para obter repositório de Payment."""
    return PaymentRepositoryImpl()
