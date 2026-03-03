"""
Create Invoice Use Case - Application Layer
==========================================

Use Case para criação de Invoice.

CARACTERÍSTICAS:
- Recebe um DTO de entrada
- Orquestra o agregado (não tem regras de negócio)
- Dispara eventos de domínio
- Salva através do repositório

Use Cases devem:
- Ser magros (thin)
- Não conter regras de negócio (isso é responsabilidade do domínio)
- Orquestrar fluxos
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional, List

from ...domain.aggregates.invoice_aggregate import InvoiceAggregate
from ...domain.repositories.invoice_repository import InvoiceRepository
from ...domain.value_objects.money import Money


@dataclass
class CreateInvoiceInputDTO:
    """
    DTO de entrada para criação de invoice.
    
    Contém os dados necessários para criar uma invoice.
    """
    customer_id: str
    due_date: Optional[str] = None
    items: Optional[List[dict]] = None


@dataclass
class CreateInvoiceOutputDTO:
    """
    DTO de saída para criação de invoice.
    
    Contém os dados da invoice criada.
    """
    invoice_id: str
    customer_id: str
    status: str
    total: str
    item_count: int
    due_date: Optional[str]
    created_at: str


class CreateInvoiceUseCase:
    """
    Use Case para criar uma nova Invoice.
    
    Este use case ORQUESTRA o fluxo:
    1. Recebe os dados de entrada (DTO)
    2. Cria o agregado (via factory)
    3. Adiciona itens (se fornecidos)
    4. Dispara eventos de domínio
    5. Persiste o agregado
    
    Observe que as REGRAS DE NEGÓCIO estão no domínio,
    não no use case.
    """
    
    def __init__(self, repository: InvoiceRepository):
        """
        Inicializa o use case com o repositório.
        
        Args:
            repository: Implementação de InvoiceRepository
        """
        self.repository = repository
    
    async def execute(self, input_dto: CreateInvoiceInputDTO) -> CreateInvoiceOutputDTO:
        """
        Executa o use case.
        
        Args:
            input_dto: Dados de entrada
            
        Returns:
            DTO com dados da invoice criada
            
        Raises:
            ValueError: Se os dados forem inválidos
        """
        # Parse customer_id
        customer_id = UUID(input_dto.customer_id)
        
        # Parse due_date
        due_date = None
        if input_dto.due_date:
            due_date = datetime.fromisoformat(input_dto.due_date)
        
        # Cria o agregado (via factory - domínio faz as validações)
        aggregate = InvoiceAggregate.create(
            customer_id=customer_id,
            due_date=due_date
        )
        
        # Adiciona itens se fornecidos
        if input_dto.items:
            for item in input_dto.items:
                # Parse do preço
                price = Money.from_float(float(item["unit_price"]))
                
                aggregate.add_item(
                    description=item["description"],
                    quantity=int(item["quantity"]),
                    unit_price=price
                )
        
        # Persiste o agregado
        saved_aggregate = await self.repository.save(aggregate)
        
        # Retorna DTO de saída
        return CreateInvoiceOutputDTO(
            invoice_id=str(saved_aggregate.id),
            customer_id=str(saved_aggregate.customer_id),
            status=saved_aggregate.status,
            total=str(saved_aggregate.total),
            item_count=saved_aggregate.item_count,
            due_date=saved_aggregate.root.due_date.isoformat() if saved_aggregate.root.due_date else None,
            created_at=saved_aggregate.root.created_at.isoformat()
        )


class AddItemToInvoiceUseCase:
    """
    Use Case para adicionar item a uma Invoice.
    """
    
    def __init__(self, repository: InvoiceRepository):
        self.repository = repository
    
    async def execute(self, invoice_id: str, item_data: dict) -> CreateInvoiceOutputDTO:
        """
        Adiciona item a uma invoice existente.
        
        Args:
            invoice_id: ID da invoice
            item_data: Dados do item (description, quantity, unit_price)
            
        Returns:
            DTO com dados atualizados
        """
        # Busca a invoice
        invoice_uuid = UUID(invoice_id)
        aggregate = await self.repository.get_by_id(invoice_uuid)
        
        if not aggregate:
            raise ValueError(f"Invoice {invoice_id} não encontrada")
        
        # Adiciona item (regras de negócio estão no agregado)
        price = Money.from_float(float(item_data["unit_price"]))
        aggregate.add_item(
            description=item["description"],
            quantity=int(item["quantity"]),
            unit_price=price
        )
        
        # Persiste
        saved_aggregate = await self.repository.save(aggregate)
        
        return CreateInvoiceOutputDTO(
            invoice_id=str(saved_aggregate.id),
            customer_id=str(saved_aggregate.customer_id),
            status=saved_aggregate.status,
            total=str(saved_aggregate.total),
            item_count=saved_aggregate.item_count,
            due_date=saved_aggregate.root.due_date.isoformat() if saved_aggregate.root.due_date else None,
            created_at=saved_aggregate.root.created_at.isoformat()
        )


class CloseInvoiceUseCase:
    """
    Use Case para fechar uma Invoice.
    """
    
    def __init__(self, repository: InvoiceRepository):
        self.repository = repository
    
    async def execute(self, invoice_id: str) -> CreateInvoiceOutputDTO:
        """
        Fecha uma invoice (envia para pagamento).
        
        Args:
            invoice_id: ID da invoice
            
        Returns:
            DTO com dados da invoice fechada
        """
        invoice_uuid = UUID(invoice_id)
        aggregate = await self.repository.get_by_id(invoice_uuid)
        
        if not aggregate:
            raise ValueError(f"Invoice {invoice_id} não encontrada")
        
        # Fecha a invoice (regras de negócio estão no agregado)
        aggregate.close()
        
        # Persiste
        saved_aggregate = await self.repository.save(aggregate)
        
        return CreateInvoiceOutputDTO(
            invoice_id=str(saved_aggregate.id),
            customer_id=str(saved_aggregate.customer_id),
            status=saved_aggregate.status,
            total=str(saved_aggregate.total),
            item_count=saved_aggregate.item_count,
            due_date=saved_aggregate.root.due_date.isoformat() if saved_aggregate.root.due_date else None,
            created_at=saved_aggregate.root.created_at.isoformat()
        )

