"""Repositories for classes."""
from uuid import UUID
from typing import Optional
from domain.classes_entities import Class, ClassRepository

class ClassRepositoryImpl(ClassRepository):
    def __init__(self):
        self.db = None
    
    async def get_by_id(self, id: UUID) -> Optional[Class]:
        pass
    
    async def get_all(self) -> list[Class]:
        pass
    
    async def save(self, entity: Class) -> Class:
        return entity

_repository_instance = None

def get_class_repository() -> ClassRepositoryImpl:
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = ClassRepositoryImpl()
    return _repository_instance
