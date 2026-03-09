"""Repositories for training."""
from uuid import UUID
from typing import Optional
from domain.training_entities import Session, SessionRepository

class SessionRepositoryImpl(SessionRepository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[Session]:
        pass
    
    async def get_all(self) -> list[Session]:
        pass
    
    async def save(self, entity: Session) -> Session:
        return entity

_repository_instance = None

def get_session_repository() -> SessionRepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = SessionRepositoryImpl()
    return _repository_instance
