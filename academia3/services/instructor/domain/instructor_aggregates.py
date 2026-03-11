"""Aggregates for instructor."""
from .instructor_entities import Instructor

class InstructorAggregate:
    """Aggregate root for instructor."""
    def __init__(self, root: Instructor):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> Instructor:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
