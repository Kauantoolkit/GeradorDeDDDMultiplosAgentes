"""Aggregates for workouts."""
from .workouts_entities import Entity

class WorkoutsAggregate:
    """Aggregate root for workouts."""
    def __init__(self, root: Entity):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> Entity:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
