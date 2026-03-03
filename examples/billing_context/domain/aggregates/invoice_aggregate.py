"""
Invoice Aggregate - Domain Layer
================================

Aggregate Root para Invoice.

O Aggregate Root é responsável por:
- Controlar o acesso às entidades internas (InvoiceItem)
- Manter as invariantes de negócio
- Serializar/desserializar o agregado completo
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal

from ..entities.invoice import Invoice, InvoiceItem, InvoiceStatus
from ..value_objects.money import Money


class InvoiceAggregate:
    """
    Aggregate Root para Invoice.
    
    RESPONSABILIDADES:
    - Controlar acesso às entidades internas
    - Manter invariantes de negócio
    - Encapsular regras que envolvem múltiplas entidades
    """
    
    def __init__(self, invoice: Invoice):
        """
        Inicializa o agregado com uma invoice.
        
        Args:
            invoice: Invoice raiz do agregado
        """
        self._invoice = invoice
    
    # ============================================================
    # PROPRIEDADES PÚBLICAS (somente leitura)
    # ============================================================
    
    @property
    def root(self) -> Invoice:
        """Retorna a raiz do agregado (Invoice)."""
        return self._invoice
    
    @property
    def id(self) -> UUID:
        """Retorna o ID da invoice."""
        return self._invoice.id
    
    @property
    def customer_id(self) -> UUID:
        """Retorna o ID do cliente."""
        return self._invoice.customer_id
    
    @property
    def status(self) -> str:
        """Retorna o status da invoice."""
        return self._invoice.status
    
    @property
    def total(self) -> Money:
        """Retorna o total da invoice."""
        return self._invoice.total
    
    @property
    def is_paid(self) -> bool:
        """Verifica se está paga."""
        return self._invoice.is_paid
    
    @property
    def is_open(self) -> bool:
        """Verifica se está aberta."""
        return self._invoice.is_open
    
    @property
    def item_count(self) -> int:
        """Retorna quantidade de itens."""
        return self._invoice.item_count
    
    # ============================================================
    # COMPORTAMENTOS DO AGREGADO
    # ============================================================
    
    def add_item(self, description: str, quantity: int, unit_price: Money) -> None:
        """
        Adiciona item ao agregado.
        
        O agregado valida:
        - Invoice não está fechada
        - Quantidade positiva
        - Preço positivo
        """
        self._invoice.add_item(description, quantity, unit_price)
    
    def remove_item(self, item_id: UUID) -> None:
        """Remove item do agregado."""
        self._invoice.remove_item(item_id)
    
    def close(self) -> None:
        """
        Fecha a invoice para pagamento.
        
        O agregado valida:
        - Invoice tem pelo menos um item
        - Invoice tem data de vencimento
        """
        self._invoice.close()
    
    def pay(self) -> None:
        """
        Marca a invoice como paga.
        
        Este método pode gerar Domain Events (implementação futura).
        """
        self._invoice.mark_as_paid()
    
    def cancel(self) -> None:
        """Cancela a invoice."""
        self._invoice.cancel()
    
    # ============================================================
    # INVARIANTES DO AGREGADO
    # ============================================================
    
    def can_add_item(self) -> bool:
        """Verifica se pode adicionar itens."""
        return self._invoice.is_draft or self._invoice.is_open
    
    def can_modify(self) -> bool:
        """Verifica se pode modificar."""
        return self._invoice.is_draft
    
    def can_cancel(self) -> bool:
        """Verifica se pode cancelar."""
        return not self._invoice.is_paid
    
    def requires_items_to_close(self) -> bool:
        """Verifica se precisa de itens para fechar."""
        return self._invoice.item_count == 0
    
    # ============================================================
    # SERIALIZAÇÃO
    # ============================================================
    
    def to_dict(self) -> dict:
        """
        Converte o agregado para dicionário.
        
        Usado para persistência.
        """
        return {
            "id": str(self._invoice.id),
            "customer_id": str(self._invoice.customer_id),
            "status": self._invoice.status,
            "total": str(self._invoice.total),
            "items": [
                {
                    "id": str(item.id),
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                    "total": str(item.total),
                }
                for item in self._invoice.items
            ],
            "due_date": self._invoice.due_date.isoformat() if self._invoice.due_date else None,
            "created_at": self._invoice.created_at.isoformat(),
            "updated_at": self._invoice.updated_at.isoformat(),
        }
    
    @staticmethod
    def from_dict(data: dict) -> "InvoiceAggregate":
        """
        Cria um agregado a partir de dicionário.
        
        Usado para reconstituir de persistência.
        """
        invoice = Invoice(
            id=UUID(data["id"]),
            customer_id=UUID(data["customer_id"]),
            status=data["status"],
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
        
        # Reconstitui itens
        for item_data in data.get("items", []):
            invoice.add_item(
                description=item_data["description"],
                quantity=item_data["quantity"],
                unit_price=Money(Decimal(str(item_data["unit_price"].replace("R$ ", "").replace(",", "."))))
            )
        
        return InvoiceAggregate(invoice)
    
    # ============================================================
    # FACTORY METHODS
    # ============================================================
    
    @staticmethod
    def create(customer_id: UUID, due_date: datetime = None) -> "InvoiceAggregate":
        """
        Factory method para criar um novo agregado.
        
        Args:
            customer_id: ID do cliente
            due_date: Data de vencimento (opcional)
            
        Returns:
            Novo InvoiceAggregate
        """
        invoice = Invoice.create(customer_id, due_date)
        return InvoiceAggregate(invoice)
    
    @staticmethod
    def create_for_customer(
        customer_id: UUID, 
        items: list[dict],
        due_date: datetime = None
    ) -> "InvoiceAggregate":
        """
        Factory method completo para criar invoice com itens.
        
        Args:
            customer_id: ID do cliente
            items: Lista de dicts com description, quantity, unit_price
            due_date: Data de vencimento
            
        Returns:
            Novo InvoiceAggregate com items
        """
        aggregate = InvoiceAggregate.create(customer_id, due_date)
        
        for item in items:
            aggregate.add_item(
                description=item["description"],
                quantity=item["quantity"],
                unit_price=Money(Decimal(str(item["unit_price"])))
            )
        
        return aggregate

