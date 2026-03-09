"""Aggregates for payment."""
from .payment_entities import Invoice

class PaymentAggregate:
    """Aggregate root for payment."""
    def __init__(self, root: Invoice):
        self._root = root
        self._entities = [root]
    
    @property
    def root(self) -> Invoice:
        return self._root
    
    def add_entity(self, entity):
        self._entities.append(entity)
