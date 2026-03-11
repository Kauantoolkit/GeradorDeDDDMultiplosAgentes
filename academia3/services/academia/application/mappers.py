"""Mappers for academia."""
from application.dtos import UserDTO
from domain.academia_entities import User

class UserMapper:
    @staticmethod
    def to_dto(entity: User) -> UserDTO:
        return UserDTO(id=entity.id)
