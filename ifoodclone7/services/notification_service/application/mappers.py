"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import NotificationDTO, CreateNotificationDTO
from domain.notification_entities import Notification


class NotificationMapper:
    """Mapper para Notification."""
    
    @staticmethod
    def to_dto(entity: Notification) -> NotificationDTO:
        return NotificationDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: NotificationDTO) -> Notification:
        return Notification(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateNotificationDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
