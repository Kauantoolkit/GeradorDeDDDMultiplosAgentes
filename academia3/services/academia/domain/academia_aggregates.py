"""Aggregates for academia."""
from .academia_entities import User

class AcademiaAggregate:
    """Aggregate root for academia."""
    def __init__(self, root: User):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> User:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
