"""
Tests - user_domain Domain
======================
Testes unitários para entidades de user_domain.
"""

import pytest
from uuid import uuid4
from datetime import datetime


class TestUser:
    """Testes para User."""
    
    def test_create_user(self):
        """Testa criação de User."""
        from ..services.service.domain import User
        
        entity = User.create()
        assert entity.id is not None
        assert entity.created_at is not None
    
    def test_update_user(self):
        """Testa atualização de User."""
        from ..services.service.domain import User
        
        entity = User.create()
        entity.update()
        assert entity.updated_at > entity.created_at
    
    def test_to_dict(self):
        """Testa conversão para dicionário."""
        from ..services.service.domain import User
        
        entity = User.create()
        data = entity.to_dict()
        assert "id" in data
        assert "created_at" in data
