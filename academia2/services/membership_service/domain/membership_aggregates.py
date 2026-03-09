"""Aggregates for membership."""
from .membership_entities import Member

class MembershipAggregate:
    """Aggregate root for membership."""
    def __init__(self, root: Member):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> Member:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
