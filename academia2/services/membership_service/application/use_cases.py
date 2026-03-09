"""Use cases for membership."""
from uuid import UUID
from domain.membership_entities import Member

class CreateMemberUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, data: dict) -> Member:
        entity = Member.create(**data)
        return await self.repository.save(entity)

class GetMemberByIdUseCase:
    def __init__(self, repository):
        self.repository = repository
    
    async def execute(self, id: UUID) -> Member | None:
        return await self.repository.get_by_id(id)
