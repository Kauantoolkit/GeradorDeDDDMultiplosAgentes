"""
Use Cases - Application Layer
=============================
Casos de uso para o domínio notification.
"""

from uuid import UUID
from domain.notification_entities import Notification


class CreateNotificationUseCase:
    """Use case para criar Notification."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Notification:
        entity = Notification.create(**data)
        return await self.repository.save(entity)


class GetNotificationByIdUseCase:
    """Use case para buscar Notification por ID."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Notification | None:
        return await self.repository.get_by_id(id)


class UpdateNotificationUseCase:
    """Use case para atualizar Notification."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID, data: dict) -> Notification | None:
        entity = await self.repository.get_by_id(id)
        if entity:
            entity.update(**data)
            return await self.repository.save(entity)
        return None


class DeleteNotificationUseCase:
    """Use case para deletar Notification."""
    
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> bool:
        return await self.repository.delete(id)
