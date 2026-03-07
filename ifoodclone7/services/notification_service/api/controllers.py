"""
Controllers - API Layer
=======================
Controladores para notification_service.
"""

from fastapi import Depends
from infrastructure.repositories import NotificationRepositoryImpl


def get_notification_repository() -> NotificationRepositoryImpl:
    """Dependência para obter repositório de Notification."""
    return NotificationRepositoryImpl()
