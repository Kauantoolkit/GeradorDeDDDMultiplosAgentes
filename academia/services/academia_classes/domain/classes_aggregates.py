"""Aggregates for classes."""
from .classes_entities import Class

class ClassesAggregate:
    """Aggregate root for classes."""
    def __init__(self, root: Class):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> Class:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
