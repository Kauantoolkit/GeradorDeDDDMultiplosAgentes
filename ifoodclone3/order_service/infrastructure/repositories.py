from domain.entities import Order
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class OrderModel(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_id = Column(String)
    items = Column(String)

engine = create_engine('postgresql://user:password@localhost/dbname')
Session = sessionmaker(bind=engine)

class OrderRepository:
    def save(self, order: Order):
        session = Session()
        order_model = OrderModel(id=order.order_id, customer_id=order.customer_id, items=str(order.items))
        session.add(order_model)
        session.commit()
        session.close()

    def get(self, order_id):
        session = Session()
        order_model = session.query(OrderModel).filter_by(id=order_id).first()
        session.close()
        return Order(order_id=order_model.id, customer_id=order_model.customer_id, items=order_model.items)