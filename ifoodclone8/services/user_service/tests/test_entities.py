from services.user_service.domain import User
import pytest

@pytest.fixture()
def user:
    return User(id=1, name='John Doe', email='john@example.com')

def test_user(user):
    assert user.id == 1
    assert user.name == 'John Doe'
    assert user.email == 'john@example.com'