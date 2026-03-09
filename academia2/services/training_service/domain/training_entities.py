"""Entity: Session"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Session:
    """Domain entity for training."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Session":
        now = datetime.now()
        return Session(
            id=uuid4(),
            created_at=now,
            updated_at=now,
            **{k: v for k, v in kwargs.items() if k not in ['id', 'created_at', 'updated_at']}
        )
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class SessionRepository:
    """Repository interface for Session."""
    async def get_by_id(self, id: UUID) -> "Session | None":
        raise NotImplementedError
    async def get_all(self) -> list["Session"]:
        raise NotImplementedError
    async def save(self, entity: "Session") -> "Session":
        raise NotImplementedError
