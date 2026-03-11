"""DTOs for Aluno."""
from dataclasses import dataclass
from uuid import UUID

@dataclass
class AlunoDTO:
    id: UUID | None = None

@dataclass
class CreateAlunoDTO:
    pass
