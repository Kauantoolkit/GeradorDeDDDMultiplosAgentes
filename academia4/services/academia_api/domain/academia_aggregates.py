"""Aggregates for academia."""
from .academia_entities import Aluno

class AcademiaAggregate:
    """Aggregate root for academia."""
    def __init__(self, root: Aluno):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> Aluno:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
