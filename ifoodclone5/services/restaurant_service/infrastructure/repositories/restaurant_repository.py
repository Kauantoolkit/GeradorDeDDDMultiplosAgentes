from restaurant_service.domain.entities.restaurant import Restaurant
from sqlalchemy.orm import Session

class RestaurantRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, restaurant: Restaurant):
        self.db.add(restaurant)
        self.db.commit()
        self.db.refresh(restaurant)
        return restaurant

    def get(self, restaurant_id: int):
        return self.db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()