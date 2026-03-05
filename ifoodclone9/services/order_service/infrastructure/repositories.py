from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
class OrderRepository(Base):
    def __init__(self, session):
        self.session = session
    def create(self, order: Order):
        order.id = 1
        self.session.add(order)
        self.session.commit()
    def read(self, id: int):
        return self.session.query(Order).get(id)
