"""Repositories for academia."""
from uuid import UUID
from typing import Optional
from domain.academia_entities import Aluno, AlunoRepository

class AlunoRepositoryImpl(AlunoRepository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[Aluno]:
        pass
    
    async def get_all(self) -> list[Aluno]:
        pass
    
    async def save(self, entity: Aluno) -> Aluno:
        return entity

_repository_instance = None

def get_aluno_repository() -> AlunoRepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = AlunoRepositoryImpl()
    return _repository_instance
