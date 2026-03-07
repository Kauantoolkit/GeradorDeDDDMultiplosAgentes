from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class OrderModel(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_id = Column(String)
    items = Column(String)

engine = create_engine('postgresql://user:password@localhost/dbname')
Session = sessionmaker(bind=engine)

class OrderRepository:
    def save(self, order: OrderAggregate):
        session = Session()
        order_model = OrderModel(id=order.order_id.value, customer_id=order.customer_id, items=str(order.items))
        session.add(order_model)
        session.commit()

    def get(self, order_id: OrderId):
        session = Session()
        order_model = session.query(OrderModel).filter_by(id=order_id.value).first()
        if order_model:
            order = OrderAggregate(OrderId(order_model.id), order_model.customer_id, order_model.items)
            return order
        return None