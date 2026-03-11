"""DTOs for Course."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class CourseDTO:
    id: UUID | None = None

@dataclass
class CreateCourseDTO:
    pass
