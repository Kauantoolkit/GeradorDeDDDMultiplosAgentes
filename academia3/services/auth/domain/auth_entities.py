"""Entity: User"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class User:
    """Domain entity for auth."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "User":
        now = datetime.now()
        return User(
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

class UserRepository:
    """Repository interface for User."""
    async def get_by_id(self, id: UUID) -> "User | None":
        raise NotImplementedError
    async def get_all(self) -> list["User"]:
        raise NotImplementedError
    async def save(self, entity: "User") -> "User":
        raise NotImplementedError


"""Entity: Token"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Token:
    """Domain entity for auth."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Token":
        now = datetime.now()
        return Token(
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

class TokenRepository:
    """Repository interface for Token."""
    async def get_by_id(self, id: UUID) -> "Token | None":
        raise NotImplementedError
    async def get_all(self) -> list["Token"]:
        raise NotImplementedError
    async def save(self, entity: "Token") -> "Token":
        raise NotImplementedError
