from services.user_service.domain import User

class CreateUserUseCase:
    def __init__(self, user: User):
        self.user = user

    def execute(self):
        # criar usuário
        pass