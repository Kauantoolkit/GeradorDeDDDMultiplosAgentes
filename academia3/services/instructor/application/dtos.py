"""DTOs for Instructor."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class InstructorDTO:
    id: UUID | None = None

@dataclass
class CreateInstructorDTO:
    pass
