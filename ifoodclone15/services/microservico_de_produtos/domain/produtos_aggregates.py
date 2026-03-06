"""
Aggregates - Domain Layer
=========================
Agregados para o domínio produtos.
Agregado é um cluster de entidades e value objects com raiz (root entity).
"""

from uuid import UUID
from .produtos_entities import ProdutosEntity


class ProdutosAggregate:
    """
    Agregado raiz para o domínio produtos.
    Controla invariantes de negócio e transações.
    """
    
    def __init__(self, root: ProdutosEntity):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> ProdutosEntity:
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
