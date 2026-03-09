"""Entity: Class"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Class:
    """Domain entity for classes."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Class":
        now = datetime.now()
        return Class(
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

class ClassRepository:
    """Repository interface for Class."""
    async def get_by_id(self, id: UUID) -> "Class | None":
        raise NotImplementedError
    async def get_all(self) -> list["Class"]:
        raise NotImplementedError
    async def save(self, entity: "Class") -> "Class":
        raise NotImplementedError


"""Entity: Instructor"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Instructor:
    """Domain entity for classes."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Instructor":
        now = datetime.now()
        return Instructor(
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

class InstructorRepository:
    """Repository interface for Instructor."""
    async def get_by_id(self, id: UUID) -> "Instructor | None":
        raise NotImplementedError
    async def get_all(self) -> list["Instructor"]:
        raise NotImplementedError
    async def save(self, entity: "Instructor") -> "Instructor":
        raise NotImplementedError
