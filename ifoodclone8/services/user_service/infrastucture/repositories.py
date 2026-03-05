from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

class UserRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    def create(self, user: User):
        # criar usuário
        pass

    def read(self, id: int):
        # ler usuário
        pass