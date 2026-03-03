"""
Invoice Entity - Domain Layer
=============================

Entidade Invoice com comportamento e regras de negócio.
NÃO é anêmica - contém validações e regras encapsuladas.

Esta entidade faz parte do InvoiceAggregate (Aggregate Root).
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal

from ..value_objects.money import Money


class InvoiceStatus:
    """Status possíveis para uma invoice."""
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass
class InvoiceItem:
    """
    Item de Invoice - Entidade interna do agregado.
    Observe que não pode ser acessada diretamente de fora do agregado.
    """
    id: UUID
    description: str
    quantity: int
    unit_price: Money
    _total: Money = field(init=False)
    
    def __post_init__(self):
        """Calcula o total do item."""
        self._total = self.unit_price.multiply(self.quantity)
    
    @property
    def total(self) -> Money:
        """Retorna o total do item (somente leitura)."""
        return self._total


@dataclass
class Invoice:
    """
    Invoice Entity - Entidade raiz do agregado.
    
    REGRAS DE NEGÓCIO ENCAPSULADAS:
    - Invoice só pode ser paga se tiver items
    - Data de vencimento não pode ser no passado
    - Não permite modificação após status PAID ou CANCELLED
    """
    id: UUID
    customer_id: UUID
    status: str
    items: list[InvoiceItem] = field(default_factory=list)
    _total: Money = field(init=False, default_factory=lambda: Money(Decimal("0.00")))
    due_date: datetime = field(default=None)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calcula o total baseado nos items."""
        if self.items:
            total = Money(Decimal("0.00"))
            for item in self.items:
                total = total.add(item.total)
            self._total = total
    
    # ============================================================
    # COMPORTAMENTOS (não apenas getters/setters)
    # ============================================================
    
    def add_item(self, description: str, quantity: int, unit_price: Money) -> None:
        """
        Adiciona um item à invoice.
        
        REGRAS:
        - Invoice deve estar em status DRAFT ou OPEN
        - Quantidade deve ser positive
        - Preço unitário deve ser positive
        
        Raises:
            ValueError: Se as regras de negócio forem violadas
        """
        # Regra: Não pode modificar se já estiver paga ou cancelada
        if self.status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED):
            raise ValueError("Invoice está fechada e não pode ser modificada")
        
        # Regra: Quantidade deve ser positiva
        if quantity <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        
        # Regra: Preço deve ser positivo
        if unit_price.amount < 0:
            raise ValueError("Preço unitário não pode ser negativo")
        
        # Cria o item
        item = InvoiceItem(
            id=uuid4(),
            description=description,
            quantity=quantity,
            unit_price=unit_price
        )
        
        self.items.append(item)
        self._recalculate_total()
        self.updated_at = datetime.now()
    
    def remove_item(self, item_id: UUID) -> None:
        """Remove um item da invoice."""
        if self.status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED):
            raise ValueError("Invoice está fechada e não pode ser modificada")
        
        self.items = [item for item in self.items if item.id != item_id]
        self._recalculate_total()
        self.updated_at = datetime.now()
    
    def close(self) -> None:
        """
        Fecha a invoice (envia para pagamento).
        
        REGRAS:
        - Invoice deve ter pelo menos um item
        - Invoice deve ter data de vencimento
        """
        if not self.items:
            raise ValueError("Invoice sem itens não pode ser fechada")
        
        if not self.due_date:
            raise ValueError("Invoice sem data de vencimento não pode ser fechada")
        
        if self.status != InvoiceStatus.DRAFT:
            raise ValueError("Apenas invoices em rascunho podem ser fechadas")
        
        self.status = InvoiceStatus.OPEN
        self.updated_at = datetime.now()
    
    def mark_as_paid(self) -> None:
        """Marca a invoice como paga."""
        if self.status != InvoiceStatus.OPEN:
            raise ValueError("Apenas invoices abertas podem ser marcadas como pagas")
        
        self.status = InvoiceStatus.PAID
        self.updated_at = datetime.now()
    
    def cancel(self) -> None:
        """Cancela a invoice."""
        if self.status == InvoiceStatus.PAID:
            raise ValueError("Invoice já paga não pode ser cancelada")
        
        self.status = InvoiceStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def _recalculate_total(self) -> None:
        """Recalcula o total da invoice."""
        total = Money(Decimal("0.00"))
        for item in self.items:
            total = total.add(item.total)
        self._total = total
    
    # ============================================================
    # PROPRIEDADES PÚBLICAS (somente leitura)
    # ============================================================
    
    @property
    def total(self) -> Money:
        """Retorna o total da invoice (somente leitura)."""
        return self._total
    
    @property
    def is_paid(self) -> bool:
        """Verifica se a invoice está paga."""
        return self.status == InvoiceStatus.PAID
    
    @property
    def is_open(self) -> bool:
        """Verifica se a invoice está aberta."""
        return self.status == InvoiceStatus.OPEN
    
    @property
    def is_cancelled(self) -> bool:
        """Verifica se a invoice está cancelada."""
        return self.status == InvoiceStatus.CANCELLED
    
    @property
    def is_draft(self) -> bool:
        """Verifica se a invoice está em rascunho."""
        return self.status == InvoiceStatus.DRAFT
    
    @property
    def item_count(self) -> int:
        """Retorna a quantidade de itens."""
        return len(self.items)
    
    # ============================================================
    # MÉTODOS DE CONVERSÃO
    # ============================================================
    
    def to_dict(self) -> dict:
        """Converte a entidade para dicionário."""
        return {
            "id": str(self.id),
            "customer_id": str(self.customer_id),
            "status": self.status,
            "total": str(self._total),
            "item_count": self.item_count,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    # ============================================================
    # FACTORY METHODS
    # ============================================================
    
    @staticmethod
    def create(customer_id: UUID, due_date: datetime = None) -> "Invoice":
        """
        Factory method para criar uma nova invoice.
        
        Args:
            customer_id: ID do cliente
            due_date: Data de vencimento (opcional)
            
        Returns:
            Nova Invoice em status DRAFT
        """
        if due_date and due_date < datetime.now():
            raise ValueError("Data de vencimento não pode ser no passado")
        
        return Invoice(
            id=uuid4(),
            customer_id=customer_id,
            status=InvoiceStatus.DRAFT,
            due_date=due_date,
        )

