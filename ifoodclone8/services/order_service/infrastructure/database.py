from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .repositories import OrderRepository

DATABASE_URL = 'postgresql://user:password@localhost/dbname'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

order_repository = OrderRepository(SessionLocal())