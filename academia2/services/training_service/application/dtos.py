"""DTOs for Session."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class SessionDTO:
    id: UUID | None = None

@dataclass
class CreateSessionDTO:
    pass
