"""Mappers for academia."""
from application.dtos import AlunoDTO
from domain.academia_entities import Aluno

class AlunoMapper:
    @staticmethod
    def to_dto(entity: Aluno) -> AlunoDTO:
        return AlunoDTO(id=entity.id)
