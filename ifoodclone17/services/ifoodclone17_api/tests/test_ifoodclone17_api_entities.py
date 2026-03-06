"""
Tests - ifoodclone17_api Domain
======================
Testes unitários para entidades de ifoodclone17_api.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestOrdercontroller:
    """Testes para Ordercontroller."""
    
    def test_create_ordercontroller(self):
        """Testa criação de Ordercontroller."""
        from ..services.service.domain import Ordercontroller
        
        entity = Ordercontroller.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_ordercontroller(self):
        """Testa atualização de Ordercontroller."""
        from ..services.service.domain import Ordercontroller
        
        entity = Ordercontroller.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import Ordercontroller
        
        entity = Ordercontroller.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
