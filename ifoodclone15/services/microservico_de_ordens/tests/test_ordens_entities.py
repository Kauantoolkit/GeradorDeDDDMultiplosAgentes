"""
Tests - ordens Domain
======================
Testes unitários para entidades de ordens.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestOrdensEntity:
    """Testes para OrdensEntity."""
    
    def test_create_ordensentity(self):
        """Testa criação de OrdensEntity."""
        from ..services.service.domain import OrdensEntity
        
        entity = OrdensEntity.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_ordensentity(self):
        """Testa atualização de OrdensEntity."""
        from ..services.service.domain import OrdensEntity
        
        entity = OrdensEntity.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import OrdensEntity
        
        entity = OrdensEntity.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
