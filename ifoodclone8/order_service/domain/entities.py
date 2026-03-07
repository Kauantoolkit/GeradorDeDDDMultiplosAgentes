"""
Order Entity - Domain Layer
=================================
Entidade representando Order no domínio order.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Optional


@dataclass
class Order:
    """
    Entidade Order - Agrega regras de negócio e identidade.
    """
    id: UUID
    customer_id: str
    items: List[dict]
    status: str
    total: float
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(customer_id: str, items: List[dict]) -> "Order":
        """Factory method para criar uma nova Order."""
        now = datetime.now()
        total = sum(item.get('price', 0) * item.get('quantity', 1) for item in items)
        return Order(
            id=uuid4(),
            customer_id=customer_id,
            items=items,
            status="PENDING",
            total=total,
            created_at=now,
            updated_at=now
        )
    
    def add_item(self, item: dict) -> None:
        """Adiciona um item ao pedido."""
        self.items.append(item)
        self.total += item.get('price', 0) * item.get('quantity', 1)
        self.updated_at = datetime.now()
    
    def remove_item(self, item_id: str) -> bool:
        """Remove um item do pedido."""
        for item in self.items:
            if item.get('id') == item_id:
                self.total -= item.get('price', 0) * item.get('quantity', 1)
                self.items.remove(item)
                self.updated_at = datetime.now()
                return True
        return False
    
    def calculate_total(self) -> float:
        """Calcula o total do pedido."""
        return sum(item.get('price', 0) * item.get('quantity', 1) for item in self.items)
    
    def can_cancel(self) -> bool:
        """Verifica se o pedido pode ser cancelado."""
        return self.status in ['PENDING', 'CONFIRMED']
    
    def cancel(self) -> bool:
        """Cancela o pedido."""
        if self.can_cancel():
            self.status = 'CANCELLED'
            self.updated_at = datetime.now()
            return True
        return False
    
    def confirm(self) -> None:
        """Confirma o pedido."""
        self.status = 'CONFIRMED'
        self.updated_at = datetime.now()
    
    def complete(self) -> None:
        """Marca o pedido como completo."""
        self.status = 'COMPLETED'
        self.updated_at = datetime.now()
    
    def update(self, **kwargs):
        """Atualiza os atributos da entidade."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Converte a entidade para dicionário."""
        return {
            "id": str(self.id),
            "customer_id": self.customer_id,
            "items": self.items,
            "status": self.status,
            "total": self.total,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# Repositório (interface)
class OrderRepository:
    """Interface para repositório de Order."""
    
    async def get_by_id(self, id: UUID) -> Optional[Order]:
        raise NotImplementedError
    
    async def get_all(self) -> List[Order]:
        raise NotImplementedError
    
    async def save(self, entity: Order) -> Order:
        raise NotImplementedError
    
    async def delete(self, id: UUID) -> bool:
        raise NotImplementedError


"""
OrderItem Entity - Domain Layer
=================================
Entidade representando OrderItem no domínio order.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class OrderItem:
    """
    Entidade OrderItem - Itens de um pedido.
    """
    id: UUID
    order_id: UUID
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(order_id: UUID, product_id: str, product_name: str, quantity: int, unit_price: float) -> "OrderItem":
        """Factory method para criar um novo OrderItem."""
        now = datetime.now()
        return OrderItem(
            id=uuid4(),
            order_id=order_id,
            product_id=product_id,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            created_at=now,
            updated_at=now
        )
    
    def get_subtotal(self) -> float:
        """Retorna o subtotal do item."""
        return self.quantity * self.unit_price
    
    def update_quantity(self, quantity: int) -> None:
        """Atualiza a quantidade do item."""
        self.quantity = quantity
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Converte a entidade para dicionário."""
        return {
            "id": str(self.id),
            "order_id": str(self.order_id),
            "product_id": self.product_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "subtotal": self.get_subtotal(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class OrderItemRepository:
    """Interface para repositório de OrderItem."""
    
    async def get_by_id(self, id: UUID) -> Optional[OrderItem]:
        raise NotImplementedError
    
    async def get_by_order_id(self, order_id: UUID) -> List[OrderItem]:
        raise NotImplementedError
    
    async def save(self, entity: OrderItem) -> OrderItem:
        raise NotImplementedError
    
    async def delete(self, id: UUID) -> bool:
        raise NotImplementedError

