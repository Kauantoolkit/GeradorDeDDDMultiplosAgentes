"""DTOs for Usuario."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class UsuarioDTO:
    id: UUID | None = None

@dataclass
class CreateUsuarioDTO:
    pass
