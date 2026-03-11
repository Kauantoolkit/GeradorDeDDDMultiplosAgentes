"""Mappers for auth."""
from application.dtos import UserDTO
from domain.auth_entities import User

class UserMapper:
    @staticmethod
    def to_dto(entity: User) -> UserDTO:
        return UserDTO(id=entity.id)
