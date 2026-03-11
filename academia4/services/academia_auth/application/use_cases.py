"""Use cases for auth."""
from uuid import UUID
from domain.auth_entities import Usuario

class CreateUsuarioUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Usuario:
        entity = Usuario.create(**data)
        return await self.repository.save(entity)

class GetUsuarioByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Usuario | None:
        return await self.repository.get_by_id(id)
