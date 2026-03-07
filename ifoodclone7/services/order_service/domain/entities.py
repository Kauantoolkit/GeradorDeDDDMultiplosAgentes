from domain.value_objects import OrderId, CustomerId, RestaurantId, OrderItem

class Order:
    def __init__(self, order_id: OrderId, customer_id: CustomerId, restaurant_id: RestaurantId, items: List[OrderItem]):
        self.order_id = order_id
        self.customer_id = customer_id
        self.restaurant_id = restaurant_id
        self.items = items

    def add_item(self, item: OrderItem):
        self.items.append(item)

    def remove_item(self, item: OrderItem):
        self.items.remove(item)

    def get_total(self):
        total = 0
        for item in self.items:
            total += item.quantity * item.product.price
        return total
