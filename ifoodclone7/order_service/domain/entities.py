from domain.value_objects import OrderId, CustomerId, RestaurantId, OrderItem

class Order:
    def __init__(self, order_id: OrderId, customer_id: CustomerId, restaurant_id: RestaurantId, items: List[OrderItem]):
        self.order_id = order_id
        self.customer_id = customer_id
        self.restaurant_id = restaurant_id
        self.items = items

class OrderItem:
    def __init__(self, product_id: UUID, quantity: int):
        self.product_id = product_id
        self.quantity = quantity
