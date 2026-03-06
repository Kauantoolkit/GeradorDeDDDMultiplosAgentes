# microservico_de_ordens - Domain Layer
from .ordens_entities import OrdensEntity, OrdensEntityRepository
from .ordens_value_objects import Address, Email, Money
from .ordens_aggregates import OrdensAggregate
