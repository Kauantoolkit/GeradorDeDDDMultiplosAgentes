"""
Infrastructure - Repositories
=============================
Implementação dos repositórios para persistência de dados.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
from typing import Optional, List

Base = declarative_base()

# Tabela de associação para itens do pedido
order_item_table = Table(
    'order_item',
    Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('quantity', Integer, nullable=False, default=1),
    Column('unit_price', Float, nullable=False, default=0.0)
)


class OrderModel(Base):
    """Modelo de banco de dados para Order."""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default='PENDING')
    total = Column(Float, nullable=False, default=0.0)
    notes = Column(String(500), nullable=True)
    delivery_address = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    items = relationship('ProductModel', secondary=order_item_table, back_populates='orders')


class ProductModel(Base):
    """Modelo de banco de dados para Product."""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    orders = relationship('OrderModel', secondary=order_item_table, back_populates='items')


class OrderRepository:
    """Implementação do repositório de pedidos."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, order_data: dict) -> dict:
        """Salva um novo pedido."""
        order = OrderModel(
            customer_id=order_data.get('customer_id', ''),
            status=order_data.get('status', 'PENDING'),
            total=order_data.get('total', 0.0),
            notes=order_data.get('notes'),
            delivery_address=str(order_data.get('delivery_address', {})) if order_data.get('delivery_address') else None
        )
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        
        # Salva os itens do pedido
        items = order_data.get('items', [])
        for item in items:
            product = self.session.query(ProductModel).filter_by(id=item.get('product_id')).first()
            if product:
                order.items.append(product)
        
        self.session.commit()
        
        return self._to_dict(order)
    
    def get_by_id(self, order_id: int) -> Optional[dict]:
        """Busca um pedido pelo ID."""
        order = self.session.query(OrderModel).filter_by(id=order_id).first()
        if order:
            return self._to_dict(order)
        return None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Busca todos os pedidos."""
        orders = self.session.query(OrderModel).offset(skip).limit(limit).all()
        return [self._to_dict(order) for order in orders]
    
    def update(self, order_id: int, order_data: dict) -> Optional[dict]:
        """Atualiza um pedido."""
        order = self.session.query(OrderModel).filter_by(id=order_id).first()
        if order:
            for key, value in order_data.items():
                if hasattr(order, key):
                    setattr(order, key, value)
            order.updated_at = datetime.now()
            self.session.commit()
            self.session.refresh(order)
            return self._to_dict(order)
        return None
    
    def delete(self, order_id: int) -> bool:
        """Remove um pedido."""
        order = self.session.query(OrderModel).filter_by(id=order_id).first()
        if order:
            self.session.delete(order)
            self.session.commit()
            return True
        return False
    
    def _to_dict(self, order: OrderModel) -> dict:
        """Converte o modelo para dicionário."""
        return {
            'id': order.id,
            'customer_id': order.customer_id,
            'status': order.status,
            'total': order.total,
            'notes': order.notes,
            'delivery_address': order.delivery_address,
            'items': [{'product_id': item.id, 'name': item.name, 'price': item.price} for item in order.items],
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'updated_at': order.updated_at.isoformat() if order.updated_at else None
        }


class ProductRepository:
    """Implementação do repositório de produtos."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, product_data: dict) -> dict:
        """Salva um novo produto."""
        product = ProductModel(
            name=product_data.get('name', ''),
            description=product_data.get('description'),
            price=product_data.get('price', 0.0),
            stock=product_data.get('stock', 0)
        )
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return self._to_dict(product)
    
    def get_by_id(self, product_id: int) -> Optional[dict]:
        """Busca um produto pelo ID."""
        product = self.session.query(ProductModel).filter_by(id=product_id).first()
        if product:
            return self._to_dict(product)
        return None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Busca todos os produtos."""
        products = self.session.query(ProductModel).offset(skip).limit(limit).all()
        return [self._to_dict(product) for product in products]
    
    def update_stock(self, product_id: int, quantity: int) -> bool:
        """Atualiza o estoque de um produto."""
        product = self.session.query(ProductModel).filter_by(id=product_id).first()
        if product:
            product.stock += quantity
            product.updated_at = datetime.now()
            self.session.commit()
            return True
        return False
    
    def _to_dict(self, product: ProductModel) -> dict:
        """Converte o modelo para dicionário."""
        return {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock,
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None
        }

