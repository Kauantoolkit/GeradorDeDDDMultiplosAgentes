"""
Mappers - Application Layer
==========================
Mapeamento entre entidades e DTOs.
"""

from application.dtos import UserDTO, CreateUserDTO
from domain.ifoodclone14_entities import User


class UserMapper:
    """Mapper para User."""
    
    @staticmethod
    def to_dto(entity: User) -> UserDTO:
        return UserDTO(
            id=entity.id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
    
    @staticmethod
    def to_entity(dto: UserDTO) -> User:
        return User(**{
            "id": dto.id,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at,
        })
    
    @staticmethod
    def to_create_dict(dto: CreateUserDTO) -> dict:
        return {k: v for k, v in dto.__dict__.items() if v is not None}
