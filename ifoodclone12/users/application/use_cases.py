from users.domain.entities import User
class CreateUserUseCase:
    def __init__(self, user: User):
        self.user = user
    def execute(self):
        # logic to create user
        pass
