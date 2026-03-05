from services.user_service.domain import User
from pydantic import BaseModel
class CreateUserUseCase:
    def __init__(self, user: User):
        self.user = user
    def execute(self):
        # Criação do usuário
        user.save()
        return user
