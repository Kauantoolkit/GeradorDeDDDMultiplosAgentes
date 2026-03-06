"""
Aggregates - Domain Layer
=========================
Agregados para o domínio ifoodclone14.
Agregado é um cluster de entidades e value objects com raiz (root entity).
"""

from uuid import UUID
from .ifoodclone14_entities import User


class Ifoodclone14Aggregate:
    """
    Agregado raiz para o domínio ifoodclone14.
    Controla invariantes de negócio e transações.
    """
    
    def __init__(self, root: User):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> User:
        return self._root
    
    def add_entity(self, entity):
        """Adiciona uma entidade ao agregado."""
        self._entities.append(entity)
    
    def remove_entity(self, entity_id: UUID) -> bool:
        """Remove uma entidade do agregado."""
        for i, e in enumerate(self._entities):
            if e.id == entity_id:
                self._entities.pop(i)
                return True
        return False
    
    def get_all_entities(self):
        """Retorna todas as entidades do agregado."""
        return self._entities.copy()
