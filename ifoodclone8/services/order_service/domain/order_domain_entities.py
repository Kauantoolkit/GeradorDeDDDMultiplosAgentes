"""
Order Entity - Domain Layer
=================================
Entidade representando Order no domínio order_domain.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Order:
    """
    Entidade Order - Agrega regras de negócio e identidade.
    """
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Order":
        """Factory method para criar uma nova Order."""
        now = datetime.now()
        return Order(
            id=uuid4(),
            created_at=now,
            updated_at=now,
            **{k: v for k, v in kwargs.items() if k not in ['id', 'created_at', 'updated_at']}
        )
    
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
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# Repositório (interface)
class OrderRepository:
    """Interface para repositório de Order."""
    
    async def get_by_id(self, id: UUID) -> Order | None:
        raise NotImplementedError
    
    async def get_all(self) -> list[Order]:
        raise NotImplementedError
    
    async def save(self, entity: Order) -> Order:
        raise NotImplementedError
    
    async def delete(self, id: UUID) -> bool:
        raise NotImplementedError
