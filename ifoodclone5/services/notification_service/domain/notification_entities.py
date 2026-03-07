"""
Notification Entity - Domain Layer
=================================
Entidade representando Notification no domínio notification.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Notification:
    """
    Entidade Notification - Agrega regras de negócio e identidade.
    """
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Notification":
        """Factory method para criar uma nova Notification."""
        now = datetime.now()
        return Notification(
            id=uuid4(),
            created_at=now,
            updated_at=now,
            **{k: v for k, v in kwargs.items() if k not in ['id', 'created_at', 'updated_at']}
        )
    
    def update(self, **kwargs):
        """Atualiza os atributos da entidade."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Converte a entidade para dicionário."""
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# Repositório (interface)
class NotificationRepository:
    """Interface para repositório de Notification."""
    
    async def get_by_id(self, id: UUID) -> Notification | None:
        raise NotImplementedError
    
    async def get_all(self) -> list[Notification]:
        raise NotImplementedError
    
    async def save(self, entity: Notification) -> Notification:
        raise NotImplementedError
    
    async def delete(self, id: UUID) -> bool:
        raise NotImplementedError


