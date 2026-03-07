from restaurant_service.domain.entities.restaurant import Restaurant

class GetRestaurantUseCase:
    def __init__(self, restaurant_repository):
        self.restaurant_repository = restaurant_repository

    def execute(self, restaurant_id):
        return self.restaurant_repository.get(restaurant_id)