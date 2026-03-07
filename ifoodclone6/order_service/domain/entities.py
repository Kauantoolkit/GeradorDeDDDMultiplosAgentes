from .value_objects import OrderId

class Order:
    def __init__(self, order_id: OrderId, customer_id: str, items: list):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = items

    def add_item(self, product_id: str, quantity: int):
        self.items.append({'product_id': product_id, 'quantity': quantity})

class OrderItem:
    def __init__(self, product_id: str, quantity: int):
        self.product_id = product_id
        self.quantity = quantity