"""
DTOs - Data Transfer Objects
===========================
Objetos para transferência de dados entre camadas.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class NotificationDTO:
    """DTO para Notification."""
    id: UUID | None = None
    nome: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class CreateNotificationDTO:
    """DTO para criação de Notification."""
    nome: str


@dataclass
class UpdateNotificationDTO:
    """DTO para atualização de Notification."""
    nome: str | None = None
