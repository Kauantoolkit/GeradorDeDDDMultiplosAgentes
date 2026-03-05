from services.user_service.application.dtos import UserDto
from services.user_service.domain import User
def map_user(user: User) -> UserDto:
    return UserDto(id=user.id, name=user.name, email=user.email)
