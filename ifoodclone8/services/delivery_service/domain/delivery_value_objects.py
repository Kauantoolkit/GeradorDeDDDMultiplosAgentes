"""
Value Objects - Domain Layer
===========================
Objetos de valor para o domínio delivery.
Objetos de valor são imutáveis e equality por valor.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Address:
    """Value Object para endereço."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "Brasil"
    
    def __str__(self) -> str:
        return f"{self.street}, {self.city} - {self.state}"


@dataclass(frozen=True)
class Email:
    """Value Object para email com validação."""
    value: str
    
    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError("Email inválido")
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Money:
    """Value Object para valores monetários."""
    amount: float
    currency: str = "BRL"
    
    def __str__(self) -> str:
        return f"R$ {self.amount:.2f}"
