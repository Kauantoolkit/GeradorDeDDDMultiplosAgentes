"""DTOs for User."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class UserDTO:
    id: UUID | None = None

@dataclass
class CreateUserDTO:
    pass
