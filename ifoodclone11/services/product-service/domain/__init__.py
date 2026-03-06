# Corrigido: evitar import circular em domain/__init__.py
from value_objects import ProductStatus
from aggregates import ProductAggregate
from events import ProductCreatedEvent