"""
Money Value Object - Domain Layer
==================================

Value Object Money - imutável, com validação e operações de domínio.

Value Objects são:
- Imutáveis (usar @dataclass(frozen=True))
- Comparados por valor (não por referência)
- Validados no __post_init__
- Métodos retornam NOVAS instâncias
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .money import Money


@dataclass(frozen=True)
class Money:
    """
    Value Object para valores monetários.
    
    CARACTERÍSTICAS:
    - Imutável (frozen=True)
    - Sempre positivo ou zero
    - Suporta operações de domínio (add, subtract, multiply)
    - Arredonda para 2 casas decimais
    """
    amount: Decimal
    currency: str = "BRL"
    
    def __post_init__(self):
        """Valida e normaliza o valor."""
        # Converte de float se necessário
        if isinstance(self.amount, float):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        
        # Arredonda para 2 casas decimais
        object.__setattr__(
            self, 
            'amount', 
            self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        
        # Valida que é não-negativo
        if self.amount < 0:
            raise ValueError("Valor monetário não pode ser negativo")
        
        # Valida moeda
        if not self.currency:
            raise ValueError("Moeda não pode ser vazia")
    
    # ============================================================
    # OPERações DE DOMÍNIO (retornam novas instâncias)
    # ============================================================
    
    def add(self, other: "Money") -> "Money":
        """
        Soma dois valores monetários.
        
        Args:
            other: Outro Money para somar
            
        Returns:
            Nova instância de Money com o resultado
            
        Raises:
            ValueError: Se as moedas forem diferentes
        """
        if self.currency != other.currency:
            raise ValueError(f"Não é possível somar {self.currency} com {other.currency}")
        
        return Money(
            amount=self.amount + other.amount,
            currency=self.currency
        )
    
    def subtract(self, other: "Money") -> "Money":
        """
        Subtrai dois valores monetários.
        
        Args:
            other: Outro Money para subtrair
            
        Returns:
            Nova instância de Money com o resultado
            
        Raises:
            ValueError: Se as moedas forem diferentes ou resultado negativo
        """
        if self.currency != other.currency:
            raise ValueError(f"Não é possível subtrair {self.currency} de {other.currency}")
        
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Resultado da subtração não pode ser negativo")
        
        return Money(
            amount=result,
            currency=self.currency
        )
    
    def multiply(self, multiplier: int) -> "Money":
        """
        Multiplica o valor monetário.
        
        Args:
            multiplier: Fator de multiplicação
            
        Returns:
            Nova instância de Money com o resultado
        """
        if not isinstance(multiplier, (int, float, Decimal)):
            raise TypeError("Multiplicador deve ser numérico")
        
        return Money(
            amount=self.amount * Decimal(str(multiplier)),
            currency=self.currency
        )
    
    def divide(self, divisor: int) -> "Money":
        """
        Divide o valor monetário.
        
        Args:
            divisor: Divisor
            
        Returns:
            Nova instância de Money com o resultado
            
        Raises:
            ZeroDivisionError: Se divisor for zero
        """
        if divisor == 0:
            raise ZeroDivisionError("Não é possível dividir por zero")
        
        return Money(
            amount=self.amount / Decimal(str(divisor)),
            currency=self.currency
        )
    
    def is_greater_than(self, other: "Money") -> bool:
        """Verifica se este valor é maior que outro."""
        if self.currency != other.currency:
            raise ValueError("Não é possível comparar moedas diferentes")
        return self.amount > other.amount
    
    def is_less_than(self, other: "Money") -> bool:
        """Verifica se este valor é menor que outro."""
        if self.currency != other.currency:
            raise ValueError("Não é possível comparar moedas diferentes")
        return self.amount < other.amount
    
    def is_equal(self, other: "Money") -> bool:
        """Verifica se este valor é igual a outro."""
        if self.currency != other.currency:
            raise ValueError("Não é possível comparar moedas diferentes")
        return self.amount == other.amount
    
    # ============================================================
    # REPRESENTAÇÃO
    # ============================================================
    
    def __str__(self) -> str:
        """Retorna representação em string formatada."""
        symbol = {
            "BRL": "R$",
            "USD": "$",
            "EUR": "€"
        }.get(self.currency, self.currency)
        
        return f"{symbol} {self.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def __repr__(self) -> str:
        """Retorna representação para debug."""
        return f"Money(amount={self.amount}, currency='{self.currency}')"
    
    def __hash__(self):
        """Permite uso em sets e como chave de dict."""
        return hash((self.amount, self.currency))
    
    def __eq__(self, other):
        """Compara por valor (não por referência)."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    # ============================================================
    # FACTORY METHODS
    # ============================================================
    
    @staticmethod
    def zero(currency: str = "BRL") -> "Money":
        """Cria um Money com valor zero."""
        return Money(amount=Decimal("0.00"), currency=currency)
    
    @staticmethod
    def from_float(amount: float, currency: str = "BRL") -> "Money":
        """Cria Money a partir de float."""
        return Money(amount=Decimal(str(amount)), currency=currency)
    
    @staticmethod
    def from_cents(cents: int, currency: str = "BRL") -> "Money":
        """Cria Money a partir de centavos."""
        return Money(amount=Decimal(cents) / Decimal("100"), currency=currency)

