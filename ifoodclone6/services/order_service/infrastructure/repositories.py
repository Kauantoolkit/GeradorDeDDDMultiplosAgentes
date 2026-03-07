from ..domain import OrderAggregate, OrderId

class OrderRepository:
    def save(self, order: OrderAggregate):
        # Implementação de salvamento no banco de dados
        pass

    def get(self, order_id: OrderId):
        # Implementação de busca no banco de dados
        pass