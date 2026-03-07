from .value_objects import OrderId, CustomerId, ProductId

class Order:
    def __init__(self, order_id, customer_id, items):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = items

class OrderItem:
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity