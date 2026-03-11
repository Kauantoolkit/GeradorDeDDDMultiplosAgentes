"""Aggregates for auth."""
from .auth_entities import Usuario

class AuthAggregate:
    """Aggregate root for auth."""
    def __init__(self, root: Usuario):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> Usuario:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
