"""DTOs for Member."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class MemberDTO:
    id: UUID | None = None

@dataclass
class CreateMemberDTO:
    pass
