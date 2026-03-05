from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
class UserRepository(Base):
    def __init__(self, session):
        self.session = session
    def create(self, user: User):
        user.id = 1
        self.session.add(user)
        self.session.commit()
    def read(self, id: int):
        return self.session.query(User).get(id)
