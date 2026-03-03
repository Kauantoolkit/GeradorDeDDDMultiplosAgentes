"""
Invoice Repository Interface - Domain Layer
==========================================

INTERFACE (protocolo) para repositório de Invoice.

IMPORTANTE: Esta é apenas uma INTERFACE (ABC).
A implementação concreta fica em infrastructure/repositories/

Esta separação é fundamental para:
- Dependency Inversion (DIP)
- Testabilidade (mocking)
- Acoplamento fraco
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List

from ...aggregates.invoice_aggregate import InvoiceAggregate


class InvoiceRepository(ABC):
    """
    Interface para repositório de Invoice.
    
    Define o contrato que a infraestrutura deve implementar.
    O domínio define "o que" precisa ser feito,
    a infraestrutura define "como" fazer.
    """
    
    @abstractmethod
    async def get_by_id(self, invoice_id: UUID) -> Optional[InvoiceAggregate]:
        """
        Busca uma invoice pelo ID.
        
        Args:
            invoice_id: ID da invoice
            
        Returns:
            InvoiceAggregate se encontrada, None caso contrário
        """
        pass
    
    @abstractmethod
    async def get_by_customer_id(self, customer_id: UUID) -> List[InvoiceAggregate]:
        """
        Busca todas as invoices de um cliente.
        
        Args:
            customer_id: ID do cliente
            
        Returns:
            Lista de InvoiceAggregate
        """
        pass
    
    @abstractmethod
    async def save(self, aggregate: InvoiceAggregate) -> InvoiceAggregate:
        """
        Salva (cria ou atualiza) uma invoice.
        
        Args:
            aggregate: Agregado a ser persistido
            
        Returns:
            Agregado persistido
        """
        pass
    
    @abstractmethod
    async def delete(self, invoice_id: UUID) -> bool:
        """
        Remove uma invoice.
        
        Args:
            invoice_id: ID da invoice
            
        Returns:
            True se removeu, False se não encontrou
        """
        pass
    
    @abstractmethod
    async def list_all(self) -> List[InvoiceAggregate]:
        """
        Lista todas as invoices.
        
        Returns:
            Lista de InvoiceAggregate
        """
        pass
    
    @abstractmethod
    async def find_by_status(self, status: str) -> List[InvoiceAggregate]:
        """
        Busca invoices por status.
        
        Args:
            status: Status da invoice (draft, open, paid, cancelled)
            
        Returns:
            Lista de InvoiceAggregate
        """
        pass

