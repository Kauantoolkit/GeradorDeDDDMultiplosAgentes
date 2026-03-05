from services.user_service.application.dtos import UserDTO
from services.user_service.domain import User

class UserMapper:
    def to_dto(self, user: User):
        return UserDTO(id=user.id, name=user.name, email=user.email)

    def to_domain(self, dto: UserDTO):
        return User(id=dto.id, name=dto.name, email=dto.email)