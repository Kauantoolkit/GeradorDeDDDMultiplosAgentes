"""
Value Objects - Domain Layer
===========================
Objetos de valor para o domínio order.
Objetos de valor são imutáveis e equality por valor.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
import re


@dataclass(frozen=True)
class OrderId:
    """Value Object para ID de pedido."""
    value: str
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CustomerId:
    """Value Object para ID de cliente."""
    value: str
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ProductId:
    """Value Object para ID de produto."""
    value: str
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Address:
    """Value Object para endereço."""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "Brasil"
    complement: Optional[str] = None
    
    def __post_init__(self):
        # Validação básica
        if not self.street:
            raise ValueError("Street is required")
        if not self.city:
            raise ValueError("City is required")
        if not self.state:
            raise ValueError("State is required")
        if not self.zip_code:
            raise ValueError("Zip code is required")
    
    def __str__(self) -> str:
        parts = [self.street, self.city, self.state, self.zip_code]
        if self.complement:
            parts.insert(1, self.complement)
        return ", ".join(parts)
    
    def to_dict(self) -> dict:
        return {
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "country": self.country,
            "complement": self.complement
        }


@dataclass(frozen=True)
class Email:
    """Value Object para email com validação."""
    value: str
    
    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError(f"Invalid email: {self.value}")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Valida formato de email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def __str__(self) -> str:
        return self.value
    
    def to_dict(self) -> dict:
        return {"value": self.value}


@dataclass(frozen=True)
class Money:
    """Value Object para valores monetários."""
    amount: Decimal
    currency: str = "BRL"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
    
    def __str__(self) -> str:
        if self.currency == "BRL":
            return f"R$ {self.amount:.2f}"
        return f"{self.amount:.2f} {self.currency}"
    
    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, multiplier: float) -> "Money":
        return Money(self.amount * Decimal(str(multiplier)), self.currency)
    
    def to_dict(self) -> dict:
        return {
            "amount": float(self.amount),
            "currency": self.currency
        }


@dataclass(frozen=True)
class OrderStatus:
    """Value Object para status do pedido."""
    value: str
    
    VALID_STATUSES = ["PENDING", "CONFIRMED", "PREPARING", "READY", "IN_TRANSIT", "DELIVERED", "CANCELLED"]
    
    def __post_init__(self):
        if self.value not in self.VALID_STATUSES:
            raise ValueError(f"Invalid order status: {self.value}")
    
    def __str__(self) -> str:
        return self.value
    
    def is_cancellable(self) -> bool:
        return self.value in ["PENDING", "CONFIRMED"]
    
    def is_final(self) -> bool:
        return self.value in ["DELIVERED", "CANCELLED"]
    
    def to_dict(self) -> dict:
        return {"value": self.value}


@dataclass(frozen=True)
class PhoneNumber:
    """Value Object para número de telefone."""
    value: str
    
    def __post_init__(self):
        # Remove caracteres não numéricos para validação
        digits = re.sub(r'\D', '', self.value)
        if len(digits) < 10 or len(digits) > 11:
            raise ValueError(f"Invalid phone number: {self.value}")
    
    def __str__(self) -> str:
        return self.value
    
    def to_dict(self) -> dict:
        return {"value": self.value}

