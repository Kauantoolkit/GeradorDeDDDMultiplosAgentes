"""Value Objects for course."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Address:
    """Value object for address."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "Brasil"

@dataclass(frozen=True)
class Email:
    """Value object for email."""
    value: str
    
    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError("Invalid email")

@dataclass(frozen=True)
class Money:
    """Value object for money."""
    amount: float
    currency: str = "BRL"
