"""
Controllers - API Layer
=======================
Controladores para reviews.
"""

from fastapi import Depends
from infrastructure.repositories import ReviewRepositoryImpl


def get_review_repository() -> ReviewRepositoryImpl:
    """Dependência para obter repositório de Review."""
    return ReviewRepositoryImpl()
