from domain.entities import Order

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class OrderItemModel(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(String, ForeignKey('orders.id'))
    product_id = Column(String)
    quantity = Column(Integer)

class OrderModel(Base):
    __tablename__ = 'orders'
    id = Column(String, primary_key=True)
    customer_id = Column(String)
    restaurant_id = Column(String)
    items = relationship('OrderItemModel', backref='order', lazy=True)

engine = create_engine('sqlite:///orders.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class OrderRepository:
    def save(self, order: Order):
        session = Session()
        order_model = OrderModel(id=str(order.order_id), customer_id=str(order.customer_id), restaurant_id=str(order.restaurant_id))
        for item in order.items:
            order_item_model = OrderItemModel(order_id=str(order.order_id), product_id=str(item.product_id), quantity=item.quantity)
            order_model.items.append(order_item_model)
        session.add(order_model)
        session.commit()

    def get(self, order_id: OrderId):
        session = Session()
        order_model = session.query(OrderModel).filter_by(id=str(order_id)).first()
        if order_model:
            order = Order(order_id=OrderId(order_model.id), customer_id=CustomerId(order_model.customer_id), restaurant_id=RestaurantId(order_model.restaurant_id), items=order_model.items)
            return order
        return None
