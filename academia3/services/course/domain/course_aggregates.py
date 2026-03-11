"""Aggregates for course."""
from .course_entities import Course

class CourseAggregate:
    """Aggregate root for course."""
    def __init__(self, root: Course):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> Course:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
