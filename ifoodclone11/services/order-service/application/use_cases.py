from domain import Order, Product
from value_objects import OrderStatus
from aggregates import OrderAggregate
from events import OrderCreatedEvent
from application import UseCaseBase
class CreateOrder(UseCaseBase):
    def execute(self, order_data):
        order = Order.create(order_data)
        order.save()
        return order
