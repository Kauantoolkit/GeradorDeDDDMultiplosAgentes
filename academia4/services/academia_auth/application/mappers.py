"""Mappers for auth."""
from application.dtos import UsuarioDTO
from domain.auth_entities import Usuario

class UsuarioMapper:
    @staticmethod
    def to_dto(entity: Usuario) -> UsuarioDTO:
        return UsuarioDTO(id=entity.id)
