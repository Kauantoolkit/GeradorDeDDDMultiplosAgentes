"""
Tests - customer Domain
======================
Testes unitários para entidades de customer.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestCustomer:
    """Testes para Customer."""
    
    def test_create_customer(self):
        """Testa criação de Customer."""
        from ..services.service.domain import Customer
        
        entity = Customer.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_customer(self):
        """Testa atualização de Customer."""
        from ..services.service.domain import Customer
        
        entity = Customer.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import Customer
        
        entity = Customer.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
