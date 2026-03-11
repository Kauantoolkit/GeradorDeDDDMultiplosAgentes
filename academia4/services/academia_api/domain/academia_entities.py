"""Entity: Aluno"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Aluno:
    """Domain entity for academia."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Aluno":
        now = datetime.now()
        return Aluno(
            id=uuid4(),
            created_at=now,
            updated_at=now,
            **{k: v for k, v in kwargs.items() if k not in ['id', 'created_at', 'updated_at']}
        )
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class AlunoRepository:
    """Repository interface for Aluno."""
    async def get_by_id(self, id: UUID) -> "Aluno | None":
        raise NotImplementedError
    async def get_all(self) -> list["Aluno"]:
        raise NotImplementedError
    async def save(self, entity: "Aluno") -> "Aluno":
        raise NotImplementedError


"""Entity: Treino"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Treino:
    """Domain entity for academia."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Treino":
        now = datetime.now()
        return Treino(
            id=uuid4(),
            created_at=now,
            updated_at=now,
            **{k: v for k, v in kwargs.items() if k not in ['id', 'created_at', 'updated_at']}
        )
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class TreinoRepository:
    """Repository interface for Treino."""
    async def get_by_id(self, id: UUID) -> "Treino | None":
        raise NotImplementedError
    async def get_all(self) -> list["Treino"]:
        raise NotImplementedError
    async def save(self, entity: "Treino") -> "Treino":
        raise NotImplementedError


"""Entity: Avaliacao"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class Avaliacao:
    """Domain entity for academia."""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    @staticmethod
    def create(**kwargs) -> "Avaliacao":
        now = datetime.now()
        return Avaliacao(
            id=uuid4(),
            created_at=now,
            updated_at=now,
            **{k: v for k, v in kwargs.items() if k not in ['id', 'created_at', 'updated_at']}
        )
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

class AvaliacaoRepository:
    """Repository interface for Avaliacao."""
    async def get_by_id(self, id: UUID) -> "Avaliacao | None":
        raise NotImplementedError
    async def get_all(self) -> list["Avaliacao"]:
        raise NotImplementedError
    async def save(self, entity: "Avaliacao") -> "Avaliacao":
        raise NotImplementedError
