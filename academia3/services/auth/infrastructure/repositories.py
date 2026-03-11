"""Repositories for auth."""
from uuid import UUID
from typing import Optional
from domain.auth_entities import User, UserRepository

class UserRepositoryImpl(UserRepository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[User]:
        pass
    
    async def get_all(self) -> list[User]:
        pass
    
    async def save(self, entity: User) -> User:
        return entity

_repository_instance = None

def get_user_repository() -> UserRepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = UserRepositoryImpl()
    return _repository_instance
