"""Entity: Member"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Member:
    """Domain entity for membership."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Member":
        now = datetime.now()
        return Member(
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

class MemberRepository:
    """Repository interface for Member."""
    async def get_by_id(self, id: UUID) -> "Member | None":
        raise NotImplementedError
    async def get_all(self) -> list["Member"]:
        raise NotImplementedError
    async def save(self, entity: "Member") -> "Member":
        raise NotImplementedError
