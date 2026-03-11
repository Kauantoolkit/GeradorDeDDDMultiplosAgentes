"""Use cases for academia."""
from uuid import UUID
from domain.academia_entities import Aluno

class CreateAlunoUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Aluno:
        entity = Aluno.create(**data)
        return await self.repository.save(entity)

class GetAlunoByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Aluno | None:
        return await self.repository.get_by_id(id)
