from domain import User
from database import Database
class UserRepository(Database):
    def create(self, user_data):
        user = User.create(user_data)
        self.save(user)
        return user
