"""
Tests - ifoodclone17_application Domain
======================
Testes unitários para entidades de ifoodclone17_application.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestOrderservice:
    """Testes para Orderservice."""
    
    def test_create_orderservice(self):
        """Testa criação de Orderservice."""
        from ..services.service.domain import Orderservice
        
        entity = Orderservice.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_orderservice(self):
        """Testa atualização de Orderservice."""
        from ..services.service.domain import Orderservice
        
        entity = Orderservice.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import Orderservice
        
        entity = Orderservice.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
