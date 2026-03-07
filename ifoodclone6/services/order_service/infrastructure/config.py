from ..infrastructure.repositories import OrderRepository

order_repository = OrderRepository()
order_service_adapter = OrderServiceAdapter(order_repository)