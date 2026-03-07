"""
Aggregates - Domain Layer
=========================
Agregados para o domínio order.
Agregado é um cluster de entidades e value objects com raiz (root entity).
"""

from uuid import UUID
from typing import List, Optional
from .entities import Order, OrderItem
from .value_objects import OrderStatus, Money, Address


class OrderAggregate:
    """
    Agregado raiz para o domínio order.
    Controla invariantes de negócio e transações.
    """
    
    def __init__(self, root: Order):
        self._root = root
        self._items: List[OrderItem] = []
    
    @property
    def root(self) -> Order:
        return self._root
    
    @property
    def items(self) -> List[OrderItem]:
        return self._items.copy()
    
    def add_item(self, item: OrderItem) -> None:
        """Adiciona um item ao agregado."""
        self._items.append(item)
    
    def remove_item(self, item_id: UUID) -> bool:
        """Remove um item do agregado."""
        for i, item in enumerate(self._items):
            if item.id == item_id:
                self._items.pop(i)
                return True
        return False
    
    def get_item(self, item_id: UUID) -> Optional[OrderItem]:
        """Retorna um item pelo ID."""
        for item in self._items:
            if item.id == item_id:
                return item
        return None
    
    def get_all_items(self) -> List[OrderItem]:
        """Retorna todos os itens do agregado."""
        return self._items.copy()
    
    def calculate_total(self) -> float:
        """Calcula o total do pedido."""
        return sum(item.get_subtotal() for item in self._items)
    
    def can_cancel(self) -> bool:
        """Verifica se o pedido pode ser cancelado."""
        return self._root.can_cancel()
    
    def cancel(self) -> bool:
        """Cancela o pedido e todos os seus itens."""
        if self.can_cancel():
            self._root.cancel()
            return True
        return False
    
    def confirm(self) -> None:
        """Confirma o pedido."""
        self._root.confirm()
    
    def complete(self) -> None:
        """Marca o pedido como completo."""
        self._root.complete()
    
    def to_dict(self) -> dict:
        """Converte o agregado para dicionário."""
        return {
            "order": self._root.to_dict(),
            "items": [item.to_dict() for item in self._items],
            "total": self.calculate_total()
        }


class OrderFactory:
    """Factory para criar agregados de Order."""
    
    @staticmethod
    def create_order_aggregate(customer_id: str, items: List[dict]) -> OrderAggregate:
        """Cria um novo agregado de pedido."""
        order = Order.create(customer_id, items)
        aggregate = OrderAggregate(order)
        
        # Cria os itens do pedido
        for item in items:
            order_item = OrderItem.create(
                order_id=order.id,
                product_id=item.get('product_id', ''),
                product_name=item.get('product_name', ''),
                quantity=item.get('quantity', 1),
                unit_price=item.get('price', 0.0)
            )
            aggregate.add_item(order_item)
        
        return aggregate
    
    @staticmethod
    def reconstitute_order_aggregate(order: Order, items: List[OrderItem]) -> OrderAggregate:
        """Reconstitui um agregado de pedido a partir de dados persistidos."""
        aggregate = OrderAggregate(order)
        for item in items:
            aggregate.add_item(item)
        return aggregate

