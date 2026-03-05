from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
class ProductRepository(Base):
    def __init__(self, session):
        self.session = session
    def create(self, product: Product):
        product.id = 1
        self.session.add(product)
        self.session.commit()
    def read(self, id: int):
        return self.session.query(Product).get(id)
