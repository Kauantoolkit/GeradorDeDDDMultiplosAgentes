# product_service - Domain Layer
from .product_entities import Product, ProductRepository
from .product_value_objects import Address, Email, Money
from .product_aggregates import ProductAggregate
