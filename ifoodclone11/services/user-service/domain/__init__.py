# Corrigido: evitar import circular em domain/__init__.py
from value_objects import UserStatus
from aggregates import UserAggregate
from events import UserCreatedEvent