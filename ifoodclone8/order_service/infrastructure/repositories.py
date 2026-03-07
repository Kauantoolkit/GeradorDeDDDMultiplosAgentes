from ..domain.aggregates import OrderAggregate
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

order_item = Table('order_item', Base.metadata,
    Column('order_id', Integer, ForeignKey('order.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('product.id'), primary_key=True),
    Column('quantity', Integer)
)

class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    items = relationship('Product', secondary=order_item, back_populates='orders')

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    orders = relationship('Order', secondary=order_item, back_populates='items')

class OrderRepository:
    def __init__(self, session):
        self.session = session

    def save(self, order: OrderAggregate):
        order_entity = Order(id=order.order_id.value, customer_id=order.customer_id.value)
        for item in order.items:
            order_item = Product(id=item.product_id.value, name='Product Name')
            order_entity.items.append(order_item)
        self.session.add(order_entity)
        self.session.commit()

    def get_by_id(self, order_id: OrderId):
        order_entity = self.session.query(Order).filter_by(id=order_id.value).first()
        if order_entity:
            order = OrderAggregate(OrderId(order_entity.id), CustomerId(order_entity.customer_id), [OrderItem(ProductId(item.id), item.quantity) for item in order_entity.items])
            return order
        return None