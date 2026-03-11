"""DTOs for Lesson."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class LessonDTO:
    id: UUID | None = None

@dataclass
class CreateLessonDTO:
    pass
