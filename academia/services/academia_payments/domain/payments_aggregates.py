"""Aggregates for payments."""
from .payments_entities import Payment

class PaymentsAggregate:
    """Aggregate root for payments."""
    def __init__(self, root: Payment):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> Payment:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
