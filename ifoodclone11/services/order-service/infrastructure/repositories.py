from domain import Order
from database import Database
class OrderRepository(Database):
    def create(self, order_data):
        order = Order.create(order_data)
        self.save(order)
        return order
