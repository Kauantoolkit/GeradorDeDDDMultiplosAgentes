from ifoodclone17.domain import User
from ifoodclone17.application import UseCase
class UserService(UseCase):
    def login_user(self):
        return User()
