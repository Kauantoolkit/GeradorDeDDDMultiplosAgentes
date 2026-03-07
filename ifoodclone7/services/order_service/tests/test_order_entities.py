"""
Tests - order Domain
======================
Testes unitários para entidades de order.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestOrder:
    """Testes para Order."""
    
    def test_create_order(self):
        """Testa criação de Order."""
        from ..services.service.domain import Order
        
        entity = Order.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_order(self):
        """Testa atualização de Order."""
        from ..services.service.domain import Order
        
        entity = Order.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import Order
        
        entity = Order.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
