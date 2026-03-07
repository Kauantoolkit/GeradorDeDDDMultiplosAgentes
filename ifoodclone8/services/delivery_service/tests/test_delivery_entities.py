"""
Tests - delivery Domain
======================
Testes unitários para entidades de delivery.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestDelivery:
    """Testes para Delivery."""
    
    def test_create_delivery(self):
        """Testa criação de Delivery."""
        from ..services.service.domain import Delivery
        
        entity = Delivery.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_delivery(self):
        """Testa atualização de Delivery."""
        from ..services.service.domain import Delivery
        
        entity = Delivery.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import Delivery
        
        entity = Delivery.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
