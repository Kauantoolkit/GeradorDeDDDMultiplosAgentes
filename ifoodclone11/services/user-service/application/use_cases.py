from domain import User, Address
from value_objects import UserStatus
from aggregates import UserAggregate
from events import UserCreatedEvent
from application import UseCaseBase
class CreateUser(UseCaseBase):
    def execute(self, user_data):
        user = User.create(user_data)
        user.save()
        return user
