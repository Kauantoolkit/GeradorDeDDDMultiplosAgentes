"""
Invoice Repository Implementation - Infrastructure Layer
====================================================

IMPLEMENTAÇÃO CONCRETA do repositório de Invoice.

Esta implementacao:
- Depende de framework (SQLAlchemy)
- Implementa a interface definida no dominio
- Traduz entre modelos de dominio e modelos de persistencia

IMPORTANTE: Este arquivo pode importar frameworks (SQLAlchemy, etc)
porque esta na camada de INFRAESTRUTURA.
"""

import json
from uuid import UUID
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column

from ...domain.aggregates.invoice_aggregate import InvoiceAggregate
from ...domain.entities.invoice import Invoice, InvoiceStatus
from ...domain.value_objects.money import Money
from ...domain.repositories.invoice_repository import InvoiceRepository
from ...infrastructure.database import Base


# ============================================================
# SQLAlchemy Model - Entity para Persistência
# ============================================================

class InvoiceModel(Base):
    """
    Modelo de persistência para Invoice.
    
    Este modelo é usado apenas pela infraestrutura.
    O domínio não conhece este modelo.
    """
    __tablename__ = "invoices"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    customer_id: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default=InvoiceStatus.DRAFT)
    total_amount: Mapped[str] = mapped_column(nullable=False, default="0.00")
    total_currency: Mapped[str] = mapped_column(nullable=False, default="BRL")
    due_date: Mapped[Optional[str]] = mapped_column(nullable=True)
    created_at: Mapped[str] = mapped_column(nullable=False)
    updated_at: Mapped[str] = mapped_column(nullable=False)
    # Items são armazenados como JSON
    items_json: Mapped[str] = mapped_column(nullable=False, default="[]")


class InvoiceRepositoryImpl(InvoiceRepository):
    """
    Implementação concreta de InvoiceRepository usando SQLAlchemy.
    
    Esta implementação:
    - Implementa a interface do domínio
    - Converte entre modelos de domínio e modelos de persistência
    - lida com detalhes de banco de dados
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa o repositório com a sessão do banco.
        
        Args:
            session: Sessão do SQLAlchemy
        """
        self.session = session
    
    async def get_by_id(self, invoice_id: UUID) -> Optional[InvoiceAggregate]:
        """Busca invoice por ID."""
        stmt = select(InvoiceModel).where(InvoiceModel.id == str(invoice_id))
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return self._to_aggregate(model)
    
    async def get_by_customer_id(self, customer_id: UUID) -> List[InvoiceAggregate]:
        """Busca todas as invoices de um cliente."""
        stmt = select(InvoiceModel).where(
            InvoiceModel.customer_id == str(customer_id)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_aggregate(m) for m in models]
    
    async def save(self, aggregate: InvoiceAggregate) -> InvoiceAggregate:
        """Salva (cria ou atualiza) uma invoice."""
        model = self._to_model(aggregate)
        
        # Verifica se já existe
        existing = await self.get_by_id(aggregate.id)
        
        if existing:
            # Update
            stmt = select(InvoiceModel).where(
                InvoiceModel.id == str(aggregate.id)
            )
            result = await self.session.execute(stmt)
            db_model = result.scalar_one()
            
            db_model.status = model.status
            db_model.total_amount = model.total_amount
            db_model.total_currency = model.total_currency
            db_model.due_date = model.due_date
            db_model.updated_at = model.updated_at
            db_model.items_json = model.items_json
        else:
            # Insert
            self.session.add(model)
        
        await self.session.commit()
        
        return aggregate
    
    async def delete(self, invoice_id: UUID) -> bool:
        """Remove uma invoice."""
        stmt = select(InvoiceModel).where(
            InvoiceModel.id == str(invoice_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return False
        
        await self.session.delete(model)
        await self.session.commit()
        
        return True
    
    async def list_all(self) -> List[InvoiceAggregate]:
        """Lista todas as invoices."""
        stmt = select(InvoiceModel)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_aggregate(m) for m in models]
    
    async def find_by_status(self, status: str) -> List[InvoiceAggregate]:
        """Busca invoices por status."""
        stmt = select(InvoiceModel).where(InvoiceModel.status == status)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        
        return [self._to_aggregate(m) for m in models]
    
    # ============================================================
    # Mappers (conversão entre camadas)
    # ============================================================
    
    def _to_model(self, aggregate: InvoiceAggregate) -> InvoiceModel:
        """Converte Aggregate para Model de persistência."""
        from datetime import datetime
        
        invoice = aggregate.root
        
        # Converte items para JSON
        items_data = []
        for item in invoice.items:
            items_data.append({
                "id": str(item.id),
                "description": item.description,
                "quantity": item.quantity,
                "unit_price_amount": str(item.unit_price.amount),
                "unit_price_currency": item.unit_price.currency,
                "total_amount": str(item.total.amount),
                "total_currency": item.total.currency,
            })
        
        return InvoiceModel(
            id=str(invoice.id),
            customer_id=str(invoice.customer_id),
            status=invoice.status,
            total_amount=str(invoice.total.amount),
            total_currency=invoice.total.currency,
            due_date=invoice.due_date.isoformat() if invoice.due_date else None,
            created_at=invoice.created_at.isoformat(),
            updated_at=invoice.updated_at.isoformat(),
            items_json=json.dumps(items_data)
        )
    
    def _to_aggregate(self, model: InvoiceModel) -> InvoiceAggregate:
        """Converte Model de persistência para Aggregate."""
        from datetime import datetime
        
        # Reconstitui a invoice
        invoice = Invoice(
            id=UUID(model.id),
            customer_id=UUID(model.customer_id),
            status=model.status,
            due_date=datetime.fromisoformat(model.due_date) if model.due_date else None,
            created_at=datetime.fromisoformat(model.created_at),
            updated_at=datetime.fromisoformat(model.updated_at),
        )
        
        # Reconstitui os items
        items_data = json.loads(model.items_json)
        for item_data in items_data:
            from ..entities.invoice import InvoiceItem
            item = InvoiceItem(
                id=UUID(item_data["id"]),
                description=item_data["description"],
                quantity=item_data["quantity"],
                unit_price=Money(
                    amount=item_data["unit_price_amount"],
                    currency=item_data["unit_price_currency"]
                )
            )
            invoice.items.append(item)
        
        return InvoiceAggregate(invoice)

