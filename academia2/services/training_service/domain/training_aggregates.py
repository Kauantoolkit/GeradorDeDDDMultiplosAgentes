"""Aggregates for training."""
from .training_entities import Session

class TrainingAggregate:
    """Aggregate root for training."""
    def __init__(self, root: Session):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> Session:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
