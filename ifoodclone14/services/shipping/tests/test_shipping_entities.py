"""
Tests - shipping Domain
======================
Testes unitários para entidades de shipping.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestAddress:
    """Testes para Address."""
    
    def test_create_address(self):
        """Testa criação de Address."""
        from ..services.service.domain import Address
        
        entity = Address.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_address(self):
        """Testa atualização de Address."""
        from ..services.service.domain import Address
        
        entity = Address.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import Address
        
        entity = Address.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
