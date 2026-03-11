"""Aggregates for lesson."""
from .lesson_entities import Lesson

class LessonAggregate:
    """Aggregate root for lesson."""
    def __init__(self, root: Lesson):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> Lesson:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
