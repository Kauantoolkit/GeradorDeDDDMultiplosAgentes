from uuid import UUID

class OrderId(UUID):
    pass

class CustomerId(UUID):
    pass

class RestaurantId(UUID):
    pass

class OrderItem:
    def __init__(self, product_id: UUID, quantity: int, product):
        self.product_id = product_id
        self.quantity = quantity
        self.product = product
