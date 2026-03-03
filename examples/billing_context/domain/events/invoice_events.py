"""
Domain Events - Domain Layer
===========================

Domain Events representam ocorrências significativas no domínio
que podem desencadear reações em outras partes do sistema.

Características:
- Imutáveis
- Contêm dados relevantes sobre o evento
- São usados para comunicação entre agregados/serviços
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from abc import ABC


class DomainEvent(ABC):
    """
    Classe base para Domain Events.
    
    Todos os eventos devem conter:
    - event_id: Identificador único
    - occurred_on: Data/hora da ocorrência
    """
    
    def __init__(self):
        self.event_id = UUID()
        self.occurred_on = datetime.now()


@dataclass
class InvoiceCreatedEvent(DomainEvent):
    """
    Evento disparado quando uma invoice é criada.
    """
    invoice_id: UUID
    customer_id: UUID
    due_date: datetime = None
    
    def __init__(self, invoice_id: UUID, customer_id: UUID, due_date: datetime = None):
        super().__init__()
        self.invoice_id = invoice_id
        self.customer_id = customer_id
        self.due_date = due_date


@dataclass
class InvoiceClosedEvent(DomainEvent):
    """
    Evento disparado quando uma invoice é fechada (enviada para pagamento).
    """
    invoice_id: UUID
    total_amount: float
    due_date: datetime
    
    def __init__(self, invoice_id: UUID, total_amount: float, due_date: datetime):
        super().__init__()
        self.invoice_id = invoice_id
        self.total_amount = total_amount
        self.due_date = due_date


@dataclass
class InvoicePaidEvent(DomainEvent):
    """
    Evento disparado quando uma invoice é marcada como paga.
    """
    invoice_id: UUID
    paid_amount: float
    paid_at: datetime
    
    def __init__(self, invoice_id: UUID, paid_amount: float, paid_at: datetime):
        super().__init__()
        self.invoice_id = invoice_id
        self.paid_amount = paid_amount
        self.paid_at = paid_at


@dataclass
class InvoiceCancelledEvent(DomainEvent):
    """
    Evento disparado quando uma invoice é cancelada.
    """
    invoice_id: UUID
    reason: str = ""
    
    def __init__(self, invoice_id: UUID, reason: str = ""):
        super().__init__()
        self.invoice_id = invoice_id
        self.reason = reason


@dataclass
class InvoiceItemAddedEvent(DomainEvent):
    """
    Evento disparado quando um item é adicionado a uma invoice.
    """
    invoice_id: UUID
    item_id: UUID
    description: str
    quantity: int
    unit_price: float
    
    def __init__(self, invoice_id: UUID, item_id: UUID, description: str, 
                 quantity: int, unit_price: float):
        super().__init__()
        self.invoice_id = invoice_id
        self.item_id = item_id
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price

