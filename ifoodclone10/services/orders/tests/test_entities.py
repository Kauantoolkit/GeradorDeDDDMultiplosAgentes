from unittest.mock import Mock
from services.orders.domain import Order
from services.orders.application import OrderUseCase
from services.orders.infrastructure import OrderRepository
from fastapi.testclient import TestClient
from services.orders.domain import OrderStatus
from services.orders.application import OrderUseCase
from services.orders.infrastructure import OrderRepository