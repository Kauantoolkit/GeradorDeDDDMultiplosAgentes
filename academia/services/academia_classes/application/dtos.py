"""DTOs for Class."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class ClassDTO:
    id: UUID | None = None

@dataclass
class CreateClassDTO:
    pass
