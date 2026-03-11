"""DTOs for Entity."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class EntityDTO:
    id: UUID | None = None

@dataclass
class CreateEntityDTO:
    pass
