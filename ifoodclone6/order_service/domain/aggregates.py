from .entities import Order, OrderItem
from .value_objects import OrderId

class OrderAggregate:
    def __init__(self, order_id, customer_id, items):
        self.order_id = order_id
        self.customer_id = customer_id
        self.items = items

    def add_item(self, product_id, quantity):
        self.items.append(OrderItem(product_id, quantity))