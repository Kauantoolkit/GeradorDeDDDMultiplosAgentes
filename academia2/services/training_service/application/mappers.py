"""Mappers for training."""
from application.dtos import SessionDTO
from domain.training_entities import Session

class SessionMapper:
    @staticmethod
    def to_dto(entity: Session) -> SessionDTO:
        return SessionDTO(id=entity.id)
