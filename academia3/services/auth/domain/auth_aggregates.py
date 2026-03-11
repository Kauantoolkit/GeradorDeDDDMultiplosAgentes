"""Aggregates for auth."""
from .auth_entities import User

class AuthAggregate:
    """Aggregate root for auth."""
    def __init__(self, root: User):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> User:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
