"""
Usercontroller Entity - Domain Layer
=================================
Entidade representando Usercontroller no domínio ifoodclone17_api.
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Usercontroller:
    """
    Entidade Usercontroller - Agrega regras de negócio e identidade.
    """
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Usercontroller":
        """Factory method para criar uma nova Usercontroller."""
        now = datetime.now()
        return Usercontroller(
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
class UsercontrollerRepository:
    """Interface para repositório de Usercontroller."""
    
    async def get_by_id(self, id: UUID) -> Usercontroller | None:
        raise NotImplementedError
    
    async def get_all(self) -> list[Usercontroller]:
        raise NotImplementedError
    
    async def save(self, entity: Usercontroller) -> Usercontroller:
        raise NotImplementedError
    
    async def delete(self, id: UUID) -> bool:
        raise NotImplementedError
