from ..application import OrderService

class OrderServiceAdapter:
    def __init__(self, order_repository):
        self.order_service = OrderService(order_repository)

    def create_order(self, order_dto):
        return self.order_service.create_order(order_dto)

    def get_order(self, order_id):
        return self.order_service.get_order(order_id)