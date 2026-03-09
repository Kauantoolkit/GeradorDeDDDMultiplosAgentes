"""Repositories for membership."""
from uuid import UUID
from typing import Optional
from domain.membership_entities import Member, MemberRepository

class MemberRepositoryImpl(MemberRepository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[Member]:
        pass
    
    async def get_all(self) -> list[Member]:
        pass
    
    async def save(self, entity: Member) -> Member:
        return entity

_repository_instance = None

def get_member_repository() -> MemberRepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = MemberRepositoryImpl()
    return _repository_instance
