"""Repositories for enrollments."""
from uuid import UUID
from typing import Optional
from domain.enrollments_entities import Entity, EntityRepository

class EntityRepositoryImpl(EntityRepository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[Entity]:
        pass
    
    async def get_all(self) -> list[Entity]:
        pass
    
    async def save(self, entity: Entity) -> Entity:
        return entity

_repository_instance = None

def get_entity_repository() -> EntityRepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = EntityRepositoryImpl()
    return _repository_instance
