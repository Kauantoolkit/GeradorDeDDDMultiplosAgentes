# Corrigido: evitar import circular em domain/__init__.py
from value_objects import OrderStatus
from aggregates import OrderAggregate
from events import OrderCreatedEvent
from infrastructure import OrderRepository