from order_service.domain.entities.order import Order
from sqlalchemy.orm import Session

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, order: Order):
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get(self, order_id: int):
        return self.db.query(Order).filter(Order.id == order_id).first()