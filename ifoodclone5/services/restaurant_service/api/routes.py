from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from restaurant_service.application.use_cases.get_restaurant_use_case import GetRestaurantUseCase
from restaurant_service.infrastructure.repositories.restaurant_repository import RestaurantRepository
from restaurant_service.api.schemas import Restaurant

router = APIRouter()

@router.get("/restaurants/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(restaurant_id: int, db: Session = Depends(RestaurantRepository.get_db)):
    use_case = GetRestaurantUseCase(RestaurantRepository(db))
    restaurant = use_case.execute(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant