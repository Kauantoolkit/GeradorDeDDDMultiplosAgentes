# customer_service - Domain Layer
from .customer_entities import Customer, CustomerRepository
from .customer_value_objects import Address, Email, Money
from .customer_aggregates import CustomerAggregate
